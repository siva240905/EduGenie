document.addEventListener("DOMContentLoaded", () => {
    // --- Global State ---
    let currentQuizData = null;
    let selectedAnswers = {};

    // Load saved API Key from localStorage
    const savedApiKey = localStorage.getItem("edugenie_api_key");
    const apiKeyInput = document.getElementById("global-api-key");
    if (savedApiKey && apiKeyInput) {
        apiKeyInput.value = savedApiKey;
    }

    // Save API key handler
    document.getElementById("save-key-btn")?.addEventListener("click", () => {
        const key = apiKeyInput.value.trim();
        localStorage.setItem("edugenie_api_key", key);
        alert(key ? "Gemini API Key saved locally!" : "API Key cleared. Running in Demo Mode.");
    });

    // Helper to get headers
    function getApiHeaders() {
        const headers = { "Content-Type": "application/json" };
        const key = apiKeyInput ? apiKeyInput.value.trim() : "";
        if (key) {
            headers["X-Gemini-API-Key"] = key;
        }
        return headers;
    }

    // Safe response JSON parser
    async function handleResponse(response) {
        const contentType = response.headers.get("content-type") || "";
        if (!response.ok) {
            if (contentType.includes("application/json")) {
                const err = await response.json();
                throw new Error(err.detail || `HTTP Error ${response.status}`);
            } else {
                throw new Error(`Server returned status ${response.status}. Please check function deployment.`);
            }
        }
        if (contentType.includes("application/json")) {
            return await response.json();
        } else {
            const rawText = await response.text();
            try {
                return JSON.parse(rawText);
            } catch (e) {
                throw new Error(`Received non-JSON response from server.`);
            }
        }
    }

    // --- Tab Navigation ---
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(target)?.classList.add("active");
        });
    });

    // --- Scenario Chips Handler ---
    document.querySelectorAll(".chip-btn").forEach(chip => {
        chip.addEventListener("click", () => {
            const scenario = chip.getAttribute("data-scenario");
            if (scenario === "ocean") {
                switchTab("tab-ask");
                document.getElementById("ask-input").value = "Which is the largest ocean?";
                document.getElementById("ask-btn").click();
            } else if (scenario === "pythagoras") {
                switchTab("tab-quiz");
                document.getElementById("quiz-topic").value = "The Pythagoras Theorem";
                document.getElementById("quiz-btn").click();
            } else if (scenario === "sql") {
                switchTab("tab-path");
                document.getElementById("path-topic").value = "SQL";
                document.getElementById("path-btn").click();
            }
        });
    });

    function switchTab(tabId) {
        tabBtns.forEach(b => {
            if (b.getAttribute("data-tab") === tabId) b.classList.add("active");
            else b.classList.remove("active");
        });
        tabPanes.forEach(p => {
            if (p.id === tabId) p.classList.add("active");
            else p.classList.remove("active");
        });
    }

    // --- 1. Q&A & Concept Explainer ---
    const askBtn = document.getElementById("ask-btn");
    const askInput = document.getElementById("ask-input");
    const askLoading = document.getElementById("ask-loading");
    const askResponseBox = document.getElementById("ask-response-box");
    const askOutput = document.getElementById("ask-output");

    askBtn?.addEventListener("click", async () => {
        const question = askInput.value.trim();
        if (!question) {
            alert("Please enter a question or concept to explain.");
            return;
        }

        const mode = document.querySelector('input[name="ask-mode"]:checked')?.value || "explain";

        askLoading.classList.remove("hidden");
        askResponseBox.classList.add("hidden");

        try {
            const response = await fetch("/api/ask", {
                method: "POST",
                headers: getApiHeaders(),
                body: JSON.stringify({ question, mode })
            });

            const data = await handleResponse(response);
            askOutput.innerHTML = typeof marked !== "undefined" ? marked.parse(data.answer) : data.answer;
            askResponseBox.classList.remove("hidden");
        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            askLoading.classList.add("hidden");
        }
    });


    // --- 2. Interactive Quiz Generator ---
    const quizBtn = document.getElementById("quiz-btn");
    const quizTopicInput = document.getElementById("quiz-topic");
    const quizDifficultySelect = document.getElementById("quiz-difficulty");
    const quizLoading = document.getElementById("quiz-loading");
    const quizContainer = document.getElementById("quiz-container");
    const quizQuestionsList = document.getElementById("quiz-questions-list");
    const submitQuizBtn = document.getElementById("submit-quiz-btn");
    const quizResultCard = document.getElementById("quiz-result-card");

    quizBtn?.addEventListener("click", async () => {
        const topic = quizTopicInput.value.trim();
        if (!topic) {
            alert("Please enter a quiz topic.");
            return;
        }

        const difficulty = quizDifficultySelect.value;
        quizLoading.classList.remove("hidden");
        quizContainer.classList.add("hidden");
        quizResultCard.classList.add("hidden");
        selectedAnswers = {};

        try {
            const response = await fetch("/api/quiz", {
                method: "POST",
                headers: getApiHeaders(),
                body: JSON.stringify({ topic, difficulty, num_questions: 4 })
            });

            currentQuizData = await handleResponse(response);
            renderQuiz(currentQuizData);
            quizContainer.classList.remove("hidden");
        } catch (error) {
            alert(`Quiz Error: ${error.message}`);
        } finally {
            quizLoading.classList.add("hidden");
        }
    });

    function renderQuiz(quiz) {
        document.getElementById("quiz-title").innerText = `Quiz: ${quiz.topic}`;
        document.getElementById("quiz-badge").innerText = (quiz.difficulty || "medium").toUpperCase();

        quizQuestionsList.innerHTML = "";

        (quiz.questions || []).forEach((q, idx) => {
            const qBox = document.createElement("div");
            qBox.className = "question-block";
            qBox.dataset.qId = q.id;

            let optionsHtml = "";
            (q.options || []).forEach((opt) => {
                optionsHtml += `
                    <div class="option-label" data-qid="${q.id}" data-opt="${escapeHtml(opt)}">
                        <i class="fa-regular fa-circle"></i>
                        <span>${escapeHtml(opt)}</span>
                    </div>
                `;
            });

            qBox.innerHTML = `
                <div class="question-title">Q${idx + 1}. ${escapeHtml(q.question)}</div>
                <div class="options-grid">${optionsHtml}</div>
                <div id="explanation-${q.id}" class="explanation-box hidden">
                    <strong>Explanation:</strong> ${escapeHtml(q.explanation)}
                </div>
            `;

            quizQuestionsList.appendChild(qBox);
        });

        // Add Option Selection Listeners
        document.querySelectorAll(".option-label").forEach(optLabel => {
            optLabel.addEventListener("click", () => {
                const qId = optLabel.getAttribute("data-qid");
                const val = optLabel.getAttribute("data-opt");

                selectedAnswers[qId] = val;

                // Toggle selected class within same question block
                document.querySelectorAll(`.option-label[data-qid="${qId}"]`).forEach(el => {
                    el.classList.remove("selected");
                    el.querySelector("i").className = "fa-regular fa-circle";
                });
                optLabel.classList.add("selected");
                optLabel.querySelector("i").className = "fa-solid fa-circle-dot";
            });
        });
    }

    // Submit Quiz Handler
    submitQuizBtn?.addEventListener("click", () => {
        if (!currentQuizData) return;

        let score = 0;
        const total = (currentQuizData.questions || []).length;

        (currentQuizData.questions || []).forEach(q => {
            const userAns = selectedAnswers[q.id];
            const correctAns = q.correct_answer;
            const expBox = document.getElementById(`explanation-${q.id}`);

            if (expBox) expBox.classList.remove("hidden");

            document.querySelectorAll(`.option-label[data-qid="${q.id}"]`).forEach(optEl => {
                const optVal = optEl.getAttribute("data-opt");
                optEl.style.pointerEvents = "none"; // Disable further clicks

                if (optVal === correctAns) {
                    optEl.classList.add("correct");
                    optEl.querySelector("i").className = "fa-solid fa-circle-check";
                    if (userAns === correctAns) {
                        score++;
                    }
                } else if (optVal === userAns && userAns !== correctAns) {
                    optEl.classList.add("incorrect");
                    optEl.querySelector("i").className = "fa-solid fa-circle-xmark";
                }
            });
        });

        // Display Score Result
        document.getElementById("score-text").innerText = `${score} / ${total}`;
        const pct = total > 0 ? Math.round((score / total) * 100) : 0;
        document.getElementById("score-progress").style.width = `${pct}%`;
        quizResultCard.classList.remove("hidden");
    });


    // --- 3. Personalized Learning Path Generator ---
    const pathBtn = document.getElementById("path-btn");
    const pathTopicInput = document.getElementById("path-topic");
    const pathLevelSelect = document.getElementById("path-level");
    const pathLoading = document.getElementById("path-loading");
    const pathContainer = document.getElementById("path-container");

    pathBtn?.addEventListener("click", async () => {
        const topic = pathTopicInput.value.trim();
        if (!topic) {
            alert("Please enter a subject or topic for the learning path.");
            return;
        }

        const level = pathLevelSelect.value;
        pathLoading.classList.remove("hidden");
        pathContainer.classList.add("hidden");

        try {
            const response = await fetch("/api/learning-path", {
                method: "POST",
                headers: getApiHeaders(),
                body: JSON.stringify({ topic, level })
            });

            const data = await handleResponse(response);
            renderLearningPath(data);
            pathContainer.classList.remove("hidden");
        } catch (error) {
            alert(`Learning Path Error: ${error.message}`);
        } finally {
            pathLoading.classList.add("hidden");
        }
    });

    function renderLearningPath(data) {
        document.getElementById("path-title").innerText = data.title || `Learning Path: ${data.topic}`;
        document.getElementById("path-time").innerHTML = `<i class="fa-regular fa-clock"></i> ${data.estimated_time || "4 weeks"}`;
        document.getElementById("path-overview").innerText = data.overview || "";

        const timeline = document.getElementById("path-stages-timeline");
        timeline.innerHTML = "";

        if (data.stages && Array.isArray(data.stages)) {
            data.stages.forEach(stg => {
                const stageDiv = document.createElement("div");
                stageDiv.className = "timeline-stage";

                const topicsHtml = (stg.topics || [])
                    .map(t => `<span class="topic-chip">${escapeHtml(t)}</span>`)
                    .join("");

                const projHtml = (stg.suggested_projects_or_exercises || [])
                    .map(p => `<div class="stage-projects"><i class="fa-solid fa-code-fork"></i> <strong>Exercise:</strong> ${escapeHtml(p)}</div>`)
                    .join("");

                stageDiv.innerHTML = `
                    <div class="timeline-node">${stg.stage_number}</div>
                    <div class="stage-card">
                        <div class="stage-header">
                            <h4>${escapeHtml(stg.title)}</h4>
                            <span class="badge badge-outline">${escapeHtml(stg.duration || "")}</span>
                        </div>
                        <div class="stage-topics-list">${topicsHtml}</div>
                        ${projHtml}
                    </div>
                `;
                timeline.appendChild(stageDiv);
            });
        }

        // Tips List
        const tipsList = document.getElementById("path-tips-list");
        tipsList.innerHTML = "";
        (data.tips_for_success || []).forEach(tip => {
            const li = document.createElement("li");
            li.innerText = tip;
            tipsList.appendChild(li);
        });
    }


    // --- 4. Summarizer ---
    const summarizeBtn = document.getElementById("summarize-btn");
    const summarizeInput = document.getElementById("summarize-input");
    const summarizeLoading = document.getElementById("summarize-loading");
    const summarizeContainer = document.getElementById("summarize-container");

    summarizeBtn?.addEventListener("click", async () => {
        const text = summarizeInput.value.trim();
        if (!text) {
            alert("Please paste text to summarize.");
            return;
        }

        summarizeLoading.classList.remove("hidden");
        summarizeContainer.classList.add("hidden");

        try {
            const response = await fetch("/api/summarize", {
                method: "POST",
                headers: getApiHeaders(),
                body: JSON.stringify({ text, max_points: 5 })
            });

            const data = await handleResponse(response);
            renderSummary(data);
            summarizeContainer.classList.remove("hidden");
        } catch (error) {
            alert(`Summarizer Error: ${error.message}`);
        } finally {
            summarizeLoading.classList.add("hidden");
        }
    });

    function renderSummary(data) {
        document.getElementById("summary-overview-text").innerText = data.summary || "";

        const takeawaysList = document.getElementById("summary-takeaways-list");
        takeawaysList.innerHTML = "";
        (data.key_takeaways || []).forEach(pt => {
            const li = document.createElement("li");
            li.innerText = pt;
            takeawaysList.appendChild(li);
        });

        const termsGrid = document.getElementById("summary-terms-grid");
        termsGrid.innerHTML = "";
        const terms = data.important_terms || [];
        
        if (terms.length === 0) {
            document.getElementById("summary-terms-section").style.display = "none";
        } else {
            document.getElementById("summary-terms-section").style.display = "block";
            terms.forEach(t => {
                const tCard = document.createElement("div");
                tCard.className = "term-card";
                tCard.innerHTML = `
                    <div class="term-title">${escapeHtml(t.term)}</div>
                    <div class="term-def">${escapeHtml(t.definition)}</div>
                `;
                termsGrid.appendChild(tCard);
            });
        }
    }

    // Helper utilities
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    window.copyToClipboard = function(elementId) {
        const el = document.getElementById(elementId);
        if (!el) return;
        navigator.clipboard.writeText(el.innerText).then(() => {
            alert("Copied to clipboard!");
        });
    };
});
