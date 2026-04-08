(() => {
    const configNode = document.getElementById("snake-frontend-config");
    if (!configNode) {
        return;
    }

    const frontendConfig = JSON.parse(configNode.textContent);

    const appState = {
        levels: [],
        levelDetails: {},
        selectedLevelId: null,
        selectedLevel: null,
        boardConfig: null,
        foodMap: {},
        snake: [],
        foods: [],
        direction: "right",
        plannedDirections: [],
        grewLastStep: false,
        desiredHarmfulCount: 0,
        pendingGrowth: 0,
        timerRemainingMs: 0,
        effectRemainingMs: 0,
        totals: {
            calories: 0,
            protein: 0,
            fat: 0,
            carb: 0,
        },
        percentages: {
            protein: 0,
            fat: 0,
            carb: 0,
        },
        currentSpeed: 0,
        running: false,
        finished: false,
        loopId: null,
        lastTickTime: 0,
        lastStepTime: 0,
        moveAccumulatorMs: 0,
        startedAtIso: null,
        latestResult: null,
        activeGameTab: "snake",
        canvasSize: 640,
        canvasDpr: 0,
        canvasSizeDirty: true,
        animationNow: 0,
        hudDirty: true,
        renderedTimerSeconds: null,
        renderedEffectSeconds: null,
        foodLayerSignature: "",
        foodLayerLayoutSignature: "",
        foodLayerDirty: true,
        boardLayoutDirty: true,
        boardBackgroundCanvas: null,
        boardBackgroundSignature: "",
        foodSpriteCache: {},
    };

    const MAX_CANVAS_DPR = 1;

    const DIRECTIONS = {
        up: { x: 0, y: -1 },
        down: { x: 0, y: 1 },
        left: { x: -1, y: 0 },
        right: { x: 1, y: 0 },
    };

    const OPPOSITE_DIRECTION = {
        up: "down",
        down: "up",
        left: "right",
        right: "left",
    };

    const KEY_TO_DIRECTION = {
        ArrowUp: "up",
        ArrowDown: "down",
        ArrowLeft: "left",
        ArrowRight: "right",
        w: "up",
        W: "up",
        s: "down",
        S: "down",
        a: "left",
        A: "left",
        d: "right",
        D: "right",
    };

    const ENABLE_SNAKE_INTERPOLATION = true;

    const REASON_LABELS = {
        wall_collision: "Столкновение со стеной",
        self_collision: "Столкновение с собой",
        chemical_wall_collision: "Столкновение со стеной во время действия колбы",
        chemical_self_collision: "Столкновение с собой во время действия колбы",
        not_enough_calories: "Не хватило калорий до конца времени",
        macro_balance_failed: "Баланс БЖУ вышел за допустимые пределы",
        calorie_overflow: "Превышен допустимый лимит калорий",
    };

    const elements = {
        gameTabs: Array.from(document.querySelectorAll("[data-game-tab]")),
        gamePanels: Array.from(document.querySelectorAll("[data-game-panel]")),
        openButton: document.getElementById("snake-open-btn"),
        openLevelsButton: document.getElementById("snake-open-levels-btn"),
        openHelpButton: document.getElementById("snake-open-help-btn"),
        modalOpenLevelsButton: document.getElementById("snake-modal-levels-btn"),
        modalOpenHelpButton: document.getElementById("snake-modal-help-btn"),
        primaryActionButton: document.getElementById("snake-primary-action-btn"),
        retryButton: document.getElementById("snake-retry-btn"),
        levelList: document.getElementById("snake-level-list"),
        legend: document.getElementById("snake-legend"),
        historyList: document.getElementById("snake-history-list"),
        selectedLevelLabel: document.getElementById("snake-selected-level-label"),
        selectedLevelGoal: document.getElementById("snake-selected-level-goal"),
        selectedLevelBalance: document.getElementById("snake-selected-level-balance"),
        gameModal: document.getElementById("snake-game-modal"),
        levelsModal: document.getElementById("snake-levels-modal"),
        helpModal: document.getElementById("snake-help-modal"),
        overlay: document.getElementById("snake-overlay"),
        overlayCard: document.getElementById("snake-overlay-card"),
        statusChip: document.getElementById("snake-status-chip"),
        timerDisplay: document.getElementById("snake-timer-display"),
        levelName: document.getElementById("snake-level-name"),
        levelCalories: document.getElementById("snake-level-calories"),
        levelBalance: document.getElementById("snake-level-target-balance"),
        calorieValue: document.getElementById("snake-calorie-value"),
        calorieMeter: document.getElementById("snake-calorie-meter"),
        calorieHelp: document.getElementById("snake-calorie-help"),
        proteinValue: document.getElementById("snake-protein-value"),
        proteinMeter: document.getElementById("snake-protein-meter"),
        proteinHelp: document.getElementById("snake-protein-help"),
        fatValue: document.getElementById("snake-fat-value"),
        fatMeter: document.getElementById("snake-fat-meter"),
        fatHelp: document.getElementById("snake-fat-help"),
        carbValue: document.getElementById("snake-carb-value"),
        carbMeter: document.getElementById("snake-carb-meter"),
        carbHelp: document.getElementById("snake-carb-help"),
        speedIndicator: document.getElementById("snake-speed-indicator"),
        effectIndicator: document.getElementById("snake-effect-indicator"),
        scoreIndicator: document.getElementById("snake-score-indicator"),
        canvas: document.getElementById("snake-canvas"),
        foodLayer: document.getElementById("snake-food-layer"),
        boardShell: document.querySelector(".snake-board-shell-modal"),
        closeButtons: Array.from(document.querySelectorAll("[data-close-modal]")),
        modalBackdrops: Array.from(document.querySelectorAll(".snake-modal-backdrop")),
    };

    const ctx = elements.canvas.getContext("2d");

    if (elements.foodLayer) {
        elements.foodLayer.style.display = "none";
        elements.foodLayer.innerHTML = "";
    }

    bindEvents();
    renderGameTabs();
    prepareCanvas();
    drawEmptyBoard();
    loadLevels();

    if (frontendConfig.user.is_authenticated) {
        loadHistory();
    }

    function bindEvents() {
        window.addEventListener("resize", () => {
            markBoardLayoutDirty();
            prepareCanvas();
            drawBoard();
        });

        document.addEventListener("keydown", handleKeyDown);

        elements.gameTabs.forEach((tab) => {
            tab.addEventListener("click", () => switchGameTab(tab.dataset.gameTab));
        });

        if (elements.openButton) {
            elements.openButton.addEventListener("click", () => openGameModal(true));
        }
        if (elements.openLevelsButton) {
            elements.openLevelsButton.addEventListener("click", () => openModal("snake-levels-modal"));
        }
        if (elements.openHelpButton) {
            elements.openHelpButton.addEventListener("click", () => openModal("snake-help-modal"));
        }
        if (elements.modalOpenLevelsButton) {
            elements.modalOpenLevelsButton.addEventListener("click", () => openModal("snake-levels-modal"));
        }
        if (elements.modalOpenHelpButton) {
            elements.modalOpenHelpButton.addEventListener("click", () => openModal("snake-help-modal"));
        }
        if (elements.primaryActionButton) {
            elements.primaryActionButton.addEventListener("click", handlePrimaryAction);
        }
        if (elements.retryButton) {
            elements.retryButton.addEventListener("click", () => {
                if (appState.selectedLevel) {
                    openGameModal(false);
                    startGame();
                }
            });
        }

        elements.closeButtons.forEach((button) => {
            button.addEventListener("click", () => closeModal(button.dataset.closeModal));
        });

        elements.modalBackdrops.forEach((modal) => {
            modal.addEventListener("click", (event) => {
                if (event.target === modal) {
                    closeModal(modal.id);
                }
            });
        });
    }

    function markBoardLayoutDirty() {
        appState.canvasSizeDirty = true;
        appState.boardLayoutDirty = true;
        appState.foodLayerDirty = true;
        appState.boardBackgroundCanvas = null;
        appState.boardBackgroundSignature = "";
        appState.foodSpriteCache = {};
    }

    function markHudDirty() {
        appState.hudDirty = true;
    }

    async function loadLevels() {
        try {
            const response = await fetch(frontendConfig.api.levels, { headers: { Accept: "application/json" } });
            if (!response.ok) {
                throw new Error("Не удалось загрузить уровни.");
            }

            const payload = await response.json();
            appState.levels = Array.isArray(payload.levels) ? payload.levels : [];
            renderLevelList();

            if (appState.levels.length) {
                await selectLevel(appState.levels[0].id, false);
            }
        } catch (error) {
            if (elements.levelList) {
                elements.levelList.innerHTML = `
                    <div class="snake-history-empty">
                        Не удалось загрузить уровни. Проверьте миграции и повторите попытку.
                    </div>
                `;
            }
        }
    }

    async function selectLevel(levelId, autoStartAfterSelection) {
        stopLoop();
        appState.selectedLevelId = levelId;
        appState.finished = false;
        appState.latestResult = null;

        try {
            if (!appState.levelDetails[levelId]) {
                const response = await fetch(`${frontendConfig.api.levels}${levelId}/`, {
                    headers: { Accept: "application/json" },
                });
                if (!response.ok) {
                    throw new Error("Не удалось загрузить уровень.");
                }

                const payload = await response.json();
                appState.levelDetails[levelId] = payload.level;
            }

            appState.selectedLevel = appState.levelDetails[levelId];
            appState.boardConfig = appState.selectedLevel.board_config;
            appState.foodMap = Object.fromEntries(
                appState.selectedLevel.foods.map((food) => [food.code, food])
            );

            updateSelectedLevelSummary();
            renderLevelList();
            renderLegend();
            resetLevelPreview(true);

            if (autoStartAfterSelection) {
                openGameModal(false);
                startGame();
            }
        } catch (error) {
            showOverlay("Ошибка уровня", "Не удалось открыть уровень", "Попробуйте выбрать другой уровень.");
        }
    }

    function renderGameTabs() {
        elements.gameTabs.forEach((tab) => {
            const isActive = tab.dataset.gameTab === appState.activeGameTab;
            tab.classList.toggle("is-active", isActive);
        });

        elements.gamePanels.forEach((panel) => {
            const isActive = panel.dataset.gamePanel === appState.activeGameTab;
            panel.classList.toggle("is-active", isActive);
        });
    }

    function switchGameTab(tabName) {
        appState.activeGameTab = tabName;
        renderGameTabs();
    }

    function updateSelectedLevelSummary() {
        if (!appState.selectedLevel) {
            elements.selectedLevelLabel.textContent = "Уровень не выбран";
            elements.selectedLevelGoal.textContent = "0 ккал";
            elements.selectedLevelBalance.textContent = "Б 0% / Ж 0% / У 0%";
            return;
        }

        elements.selectedLevelLabel.textContent = appState.selectedLevel.title;
        elements.selectedLevelGoal.textContent =
            `${appState.selectedLevel.target_calories} ккал · ${formatTime(appState.selectedLevel.time_limit_seconds)}`;
        elements.selectedLevelBalance.textContent =
            `Б ${appState.selectedLevel.target_protein_percent}% / Ж ${appState.selectedLevel.target_fat_percent}% / У ${appState.selectedLevel.target_carb_percent}%`;
    }

    function renderLevelList() {
        if (!elements.levelList) {
            return;
        }

        if (!appState.levels.length) {
            elements.levelList.innerHTML = `
                <div class="snake-placeholder-card">
                    Уровни ещё не созданы.
                </div>
            `;
            return;
        }

        elements.levelList.innerHTML = appState.levels
            .map((level) => {
                const difficultyClass =
                    level.difficulty === "hard"
                        ? "is-hard"
                        : level.difficulty === "medium"
                            ? "is-medium"
                            : "";
                const isSelected = level.id === appState.selectedLevelId;

                return `
                    <button type="button" class="snake-level-card ${isSelected ? "is-selected" : ""}" data-level-id="${level.id}">
                        <div class="snake-level-chip-row">
                            <span class="snake-chip ${difficultyClass}">${level.difficulty_label}</span>
                            <span class="snake-chip">${level.meal_type_label}</span>
                        </div>
                        <h3>${escapeHtml(level.title)}</h3>
                        <p class="mb-0">
                            Цель: ${level.target_calories} ккал<br>
                            Допуск: ${level.min_calories}-${level.max_calories} ккал
                        </p>
                        <div class="snake-level-stats">
                            <span>Б ${level.target_protein_percent}%</span>
                            <span>Ж ${level.target_fat_percent}%</span>
                            <span>У ${level.target_carb_percent}%</span>
                            <span>${formatTime(level.time_limit_seconds)}</span>
                        </div>
                    </button>
                `;
            })
            .join("");

        elements.levelList.querySelectorAll("[data-level-id]").forEach((button) => {
            button.addEventListener("click", async () => {
                const newLevelId = Number(button.dataset.levelId);
                if (newLevelId !== appState.selectedLevelId) {
                    await selectLevel(newLevelId, false);
                }
                closeModal("snake-levels-modal");
            });
        });
    }

    function renderLegend() {
        if (!elements.legend) {
            return;
        }

        const foods = appState.selectedLevel?.foods || [];
        elements.legend.innerHTML = foods
            .map((food) => {
                const nutrition = food.kind === "healthy" || food.kind === "harmful"
                    ? ` · Б ${food.protein} / Ж ${food.fat} / У ${food.carb}`
                    : "";

                return `
                    <article class="snake-legend-card">
                        <div class="snake-legend-emoji">${food.emoji}</div>
                        <div>
                            <h4>${escapeHtml(food.label)}</h4>
                            <p>${escapeHtml(food.description)}</p>
                            <p class="mb-0">${food.calories} ккал${nutrition}</p>
                        </div>
                    </article>
                `;
            })
            .join("");
    }

    function openGameModal(autoStart) {
        if (!appState.selectedLevel) {
            return;
        }

        markBoardLayoutDirty();
        openModal("snake-game-modal");

        if (autoStart) {
            startGame();
        } else {
            prepareCanvas();
            drawBoard();
        }
    }

    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            return;
        }

        modal.classList.remove("is-hidden");
        document.body.classList.add("game-modal-open");

        if (modalId === "snake-game-modal") {
            markBoardLayoutDirty();
            prepareCanvas();
            drawBoard();
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            return;
        }

        modal.classList.add("is-hidden");

        if (modalId === "snake-game-modal") {
            stopLoop();
            resetLevelPreview(false);
        }

        syncBodyLock();
    }

    function syncBodyLock() {
        const hasOpenModal = elements.modalBackdrops.some((modal) => !modal.classList.contains("is-hidden"));
        document.body.classList.toggle("game-modal-open", hasOpenModal);
    }

    function handlePrimaryAction() {
        if (!appState.selectedLevel) {
            return;
        }

        if (appState.finished && appState.latestResult?.isWin) {
            const nextLevel = getNextLevel();
            if (nextLevel) {
                selectLevel(nextLevel.id, true);
                return;
            }
        }

        if (!appState.running) {
            startGame();
        }
    }

    function startGame() {
        if (!appState.selectedLevel) {
            return;
        }

        openModal("snake-game-modal");
        resetLevelPreview(false);
        appState.running = true;
        appState.finished = false;
        appState.startedAtIso = new Date().toISOString();
        hideOverlay();
        updateStatus("Игра идёт", "is-playing");
        updateActionButtons();
        startLoop();
    }

    function resetLevelPreview(showIntroOverlay) {
        if (!appState.selectedLevel) {
            return;
        }

        const gridSize = appState.boardConfig.grid_size;
        const centerY = Math.floor(gridSize / 2);
        const initialLength = appState.boardConfig.initial_snake_length || 4;
        const headX = Math.max(Math.floor(gridSize / 4), initialLength + 1);
        appState.snake = Array.from({ length: initialLength }, (_, index) => ({
            x: headX - index,
            y: centerY,
        }));
        appState.foods = [];
        appState.direction = "right";
        appState.plannedDirections = [];
        appState.desiredHarmfulCount = randomInt(0, appState.boardConfig.max_harmful_items || 0);
        appState.grewLastStep = false;
        appState.pendingGrowth = 0;
        appState.timerRemainingMs = appState.selectedLevel.time_limit_seconds * 1000;
        appState.effectRemainingMs = 0;
        appState.running = false;
        appState.finished = false;
        appState.lastTickTime = 0;
        appState.lastStepTime = 0;
        appState.moveAccumulatorMs = 0;
        appState.startedAtIso = null;
        appState.latestResult = null;
        appState.totals = { calories: 0, protein: 0, fat: 0, carb: 0 };
        appState.percentages = { protein: 0, fat: 0, carb: 0 };
        appState.currentSpeed = Number(appState.selectedLevel.initial_speed);
        appState.hudDirty = true;
        appState.renderedTimerSeconds = null;
        appState.renderedEffectSeconds = null;
        appState.foodLayerSignature = "";
        appState.foodLayerLayoutSignature = "";
        appState.foodLayerDirty = true;
        appState.boardLayoutDirty = true;
        appState.canvasSizeDirty = true;
        appState.boardBackgroundCanvas = null;
        appState.boardBackgroundSignature = "";

        ensureFoodPopulation();
        updateHud();
        drawBoard();
        updateStatus("Ожидание старта", "is-idle");

        if (showIntroOverlay) {
            showOverlay(
                appState.selectedLevel.title,
                "Уровень готов",
                `Цель: ${appState.selectedLevel.target_calories} ккал. Нажмите «Играть», чтобы открыть окно и начать уровень.`
            );
        } else {
            showOverlay(
                appState.selectedLevel.title,
                "Нажмите «Играть»",
                "После старта таймер, калории и баланс БЖУ будут видны прямо над игровым полем."
            );
        }

        updateActionButtons();
    }

    function stopLoop() {
        appState.running = false;
        if (appState.loopId) {
            window.cancelAnimationFrame(appState.loopId);
            appState.loopId = null;
        }
    }

    function startLoop() {
        stopLoop();
        appState.running = true;
        appState.lastTickTime = 0;
        appState.lastStepTime = 0;
        appState.moveAccumulatorMs = 0;
        appState.loopId = window.requestAnimationFrame(gameLoop);
    }

    function gameLoop(now) {
        if (!appState.running) {
            return;
        }

        appState.loopId = window.requestAnimationFrame(gameLoop);
        appState.animationNow = now;

        if (!appState.lastTickTime) {
            appState.lastTickTime = now;
        }

        if (!appState.lastStepTime) {
            appState.lastStepTime = now;
        }

        const delta = Math.min(Math.max(now - appState.lastTickTime, 0), 100);
        appState.lastTickTime = now;
        appState.timerRemainingMs = Math.max(0, appState.timerRemainingMs - delta);

        const hadEffect = appState.effectRemainingMs > 0;
        appState.effectRemainingMs = Math.max(0, appState.effectRemainingMs - delta);
        appState.currentSpeed = calculateCurrentSpeed();
        const stepInterval = getCurrentStepInterval();

        if (hadEffect && appState.effectRemainingMs === 0 && appState.running) {
            appState.plannedDirections = [];
            updateStatus("Игра идёт", "is-playing");
            markHudDirty();
        }

        let elapsed = Math.max(now - appState.lastStepTime, 0);

        if (appState.running && elapsed >= stepInterval) {
            moveSnake();
            appState.lastStepTime = now;
            appState.currentSpeed = calculateCurrentSpeed();
            elapsed = 0;
        }

        appState.moveAccumulatorMs = Math.min(elapsed, stepInterval);

        if (appState.running && appState.timerRemainingMs <= 0) {
            finishByTimer();
        }

        refreshHud();
        drawBoard();
    }

    function moveSnake() {
        const nextDirection = appState.effectRemainingMs > 0
            ? getRandomDirection(appState.direction)
            : getNextDirection();
        appState.direction = nextDirection;

        const head = appState.snake[0];
        const vector = DIRECTIONS[nextDirection];
        const newHead = { x: head.x + vector.x, y: head.y + vector.y };
        const consumedFood = appState.foods.find((food) => food.x === newHead.x && food.y === newHead.y) || null;
        const willGrow = appState.pendingGrowth > 0 || Boolean(consumedFood);
        const bodyToCheck = willGrow ? appState.snake : appState.snake.slice(0, -1);
        appState.grewLastStep = willGrow;

        if (hitsWall(newHead)) {
            endGame(false, appState.effectRemainingMs > 0 ? "chemical_wall_collision" : "wall_collision");
            return;
        }

        if (bodyToCheck.some((segment) => segment.x === newHead.x && segment.y === newHead.y)) {
            endGame(false, appState.effectRemainingMs > 0 ? "chemical_self_collision" : "self_collision");
            return;
        }

        appState.snake.unshift(newHead);

        if (consumedFood) {
            consumeFood(consumedFood);
        } else if (appState.pendingGrowth > 0) {
            appState.pendingGrowth -= 1;
        } else {
            appState.snake.pop();
        }
    }

    function consumeFood(consumedFood) {
        appState.foods = appState.foods.filter((food) => food !== consumedFood);
        const food = appState.foodMap[consumedFood.code];

        if (!food) {
            return;
        }

        if (food.code === "chemistry") {
            appState.effectRemainingMs = (appState.boardConfig.chemical_effect_seconds || 5) * 1000;
            updateStatus("Эффект колбы", "is-confused");
            appState.desiredHarmfulCount = randomInt(0, appState.boardConfig.max_harmful_items || 0);
            ensureFoodPopulation();
            markHudDirty();
            return;
        }

        appState.totals.calories += Number(food.calories);
        appState.totals.protein = roundToTwo(appState.totals.protein + Number(food.protein));
        appState.totals.fat = roundToTwo(appState.totals.fat + Number(food.fat));
        appState.totals.carb = roundToTwo(appState.totals.carb + Number(food.carb));
        appState.percentages = calculateMacroPercentages();

        if (food.kind === "healthy") {
            appState.pendingGrowth += 1;
        }

        appState.desiredHarmfulCount = randomInt(0, appState.boardConfig.max_harmful_items || 0);
        ensureFoodPopulation();
        markHudDirty();

        if (appState.totals.calories > appState.selectedLevel.max_calories) {
            endGame(false, "calorie_overflow");
            return;
        }

        if (isWinState()) {
            endGame(true, "");
        }
    }

    function finishByTimer() {
        if (isWinState()) {
            endGame(true, "");
            return;
        }

        if (appState.totals.calories < appState.selectedLevel.min_calories) {
            endGame(false, "not_enough_calories");
            return;
        }

        endGame(false, "macro_balance_failed");
    }

    function endGame(isWin, loseReason) {
        stopLoop();
        appState.finished = true;
        appState.running = false;
        markHudDirty();

        updateStatus(isWin ? "Победа" : "Поражение", isWin ? "is-win" : "is-lose");

        const durationSeconds = Math.min(
            appState.selectedLevel.time_limit_seconds,
            Math.round((appState.selectedLevel.time_limit_seconds * 1000 - appState.timerRemainingMs) / 1000)
        );

        appState.latestResult = {
            isWin,
            loseReason,
            loseReasonLabel: REASON_LABELS[loseReason] || "",
            durationSeconds,
            score: estimateScore(isWin),
        };

        refreshHud(true);
        drawBoard();
        showResultOverlay();
        updateActionButtons();
        saveResult();
    }

    async function saveResult() {
        if (!appState.selectedLevel || !appState.latestResult || !frontendConfig.user.is_authenticated) {
            return;
        }

        const payload = {
            level_id: appState.selectedLevel.id,
            is_win: appState.latestResult.isWin,
            lose_reason: appState.latestResult.isWin ? "" : appState.latestResult.loseReason,
            total_calories: appState.totals.calories,
            total_protein: appState.totals.protein,
            total_fat: appState.totals.fat,
            total_carb: appState.totals.carb,
            protein_percent: appState.percentages.protein,
            fat_percent: appState.percentages.fat,
            carb_percent: appState.percentages.carb,
            duration_seconds: appState.latestResult.durationSeconds,
            started_at: appState.startedAtIso,
        };

        try {
            const response = await fetch(frontendConfig.api.result, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    Accept: "application/json",
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error("Не удалось сохранить результат.");
            }

            const data = await response.json();
            if (data.attempt) {
                appState.latestResult.score = data.attempt.score;
                updateHud();
                showResultOverlay();
            }

            loadHistory();
        } catch (error) {
            console.error(error);
        }
    }

    async function loadHistory() {
        if (!frontendConfig.user.is_authenticated || !elements.historyList) {
            return;
        }

        try {
            const response = await fetch(frontendConfig.api.history, { headers: { Accept: "application/json" } });
            if (!response.ok) {
                throw new Error("Не удалось загрузить историю.");
            }

            const payload = await response.json();
            renderHistory(payload.attempts || []);
        } catch (error) {
            elements.historyList.innerHTML = `
                <div class="snake-history-empty">
                    История временно недоступна.
                </div>
            `;
        }
    }

    function renderHistory(attempts) {
        if (!elements.historyList) {
            return;
        }

        if (!attempts.length) {
            elements.historyList.innerHTML = `
                <div class="snake-history-empty">
                    После первой завершённой игры здесь появятся результаты.
                </div>
            `;
            return;
        }

        elements.historyList.innerHTML = attempts
            .map((attempt) => {
                const resultClass = attempt.is_win ? "is-win" : "is-lose";
                const resultText = attempt.is_win ? "Победа" : attempt.lose_reason_label;
                return `
                    <article class="snake-history-item ${resultClass}">
                        <strong>${escapeHtml(attempt.level_title)}</strong>
                        <div class="snake-history-meta">
                            <span>${attempt.total_calories} ккал</span>
                            <span>Б ${attempt.protein_percent}%</span>
                            <span>Ж ${attempt.fat_percent}%</span>
                            <span>У ${attempt.carb_percent}%</span>
                        </div>
                        <p class="mb-1">${escapeHtml(resultText)}</p>
                        <small class="text-muted">${formatDateTime(attempt.finished_at)} · ${attempt.score} очков</small>
                    </article>
                `;
            })
            .join("");
    }

    function updateHud() {
        if (!appState.selectedLevel) {
            resetHud();
            return;
        }

        elements.levelName.textContent = appState.selectedLevel.title;
        elements.levelCalories.textContent =
            `${appState.selectedLevel.target_calories} ккал · ${formatTime(appState.selectedLevel.time_limit_seconds)}`;
        elements.levelBalance.textContent =
            `Б ${appState.selectedLevel.target_protein_percent}% / Ж ${appState.selectedLevel.target_fat_percent}% / У ${appState.selectedLevel.target_carb_percent}%`;

        elements.timerDisplay.textContent = formatTime(Math.ceil(appState.timerRemainingMs / 1000));
        elements.calorieValue.textContent = `${appState.totals.calories} / ${appState.selectedLevel.target_calories} ккал`;
        elements.proteinValue.textContent = `${appState.percentages.protein.toFixed(1)}%`;
        elements.fatValue.textContent = `${appState.percentages.fat.toFixed(1)}%`;
        elements.carbValue.textContent = `${appState.percentages.carb.toFixed(1)}%`;

        elements.calorieHelp.textContent =
            `Допуск: ${appState.selectedLevel.min_calories}-${appState.selectedLevel.max_calories} ккал`;
        elements.proteinHelp.textContent =
            `Цель: ${appState.selectedLevel.target_protein_percent}% · допуск ${appState.selectedLevel.min_protein_percent}-${appState.selectedLevel.max_protein_percent}%`;
        elements.fatHelp.textContent =
            `Цель: ${appState.selectedLevel.target_fat_percent}% · допуск ${appState.selectedLevel.min_fat_percent}-${appState.selectedLevel.max_fat_percent}%`;
        elements.carbHelp.textContent =
            `Цель: ${appState.selectedLevel.target_carb_percent}% · допуск ${appState.selectedLevel.min_carb_percent}-${appState.selectedLevel.max_carb_percent}%`;

        const calorieMax = Math.max(
            appState.selectedLevel.max_calories + 140,
            appState.selectedLevel.target_calories + 160
        );
        setMeter(
            elements.calorieMeter,
            (appState.totals.calories / calorieMax) * 100,
            (appState.selectedLevel.min_calories / calorieMax) * 100,
            ((appState.selectedLevel.max_calories - appState.selectedLevel.min_calories) / calorieMax) * 100,
            isBetween(appState.totals.calories, appState.selectedLevel.min_calories, appState.selectedLevel.max_calories),
            appState.totals.calories > appState.selectedLevel.max_calories
        );
        setMeter(
            elements.proteinMeter,
            appState.percentages.protein,
            appState.selectedLevel.min_protein_percent,
            appState.selectedLevel.max_protein_percent - appState.selectedLevel.min_protein_percent,
            isBetween(appState.percentages.protein, appState.selectedLevel.min_protein_percent, appState.selectedLevel.max_protein_percent),
            appState.percentages.protein > appState.selectedLevel.max_protein_percent
        );
        setMeter(
            elements.fatMeter,
            appState.percentages.fat,
            appState.selectedLevel.min_fat_percent,
            appState.selectedLevel.max_fat_percent - appState.selectedLevel.min_fat_percent,
            isBetween(appState.percentages.fat, appState.selectedLevel.min_fat_percent, appState.selectedLevel.max_fat_percent),
            appState.percentages.fat > appState.selectedLevel.max_fat_percent
        );
        setMeter(
            elements.carbMeter,
            appState.percentages.carb,
            appState.selectedLevel.min_carb_percent,
            appState.selectedLevel.max_carb_percent - appState.selectedLevel.min_carb_percent,
            isBetween(appState.percentages.carb, appState.selectedLevel.min_carb_percent, appState.selectedLevel.max_carb_percent),
            appState.percentages.carb > appState.selectedLevel.max_carb_percent
        );

        elements.speedIndicator.textContent = `Скорость: ${appState.currentSpeed.toFixed(1)}`;
        elements.effectIndicator.textContent = appState.effectRemainingMs > 0
            ? `Эффект: хаос ${Math.ceil(appState.effectRemainingMs / 1000)}с`
            : "Эффекты: нет";
        elements.scoreIndicator.textContent = `Очки: ${appState.latestResult?.score ?? estimateScore(isWinState())}`;
    }

    function refreshHud(force = false) {
        if (!appState.selectedLevel) {
            if (force || appState.hudDirty) {
                appState.hudDirty = false;
                updateHud();
            }
            return;
        }

        const timerSeconds = Math.ceil(appState.timerRemainingMs / 1000);
        const effectSeconds = appState.effectRemainingMs > 0 ? Math.ceil(appState.effectRemainingMs / 1000) : 0;
        const shouldRefresh =
            force
            || appState.hudDirty
            || timerSeconds !== appState.renderedTimerSeconds
            || effectSeconds !== appState.renderedEffectSeconds;

        if (!shouldRefresh) {
            return;
        }

        appState.renderedTimerSeconds = timerSeconds;
        appState.renderedEffectSeconds = effectSeconds;
        appState.hudDirty = false;
        updateHud();
    }

    function resetHud() {
        elements.levelName.textContent = "Уровень не выбран";
        elements.levelCalories.textContent = "0 ккал";
        elements.levelBalance.textContent = "Б 0% / Ж 0% / У 0%";
        elements.timerDisplay.textContent = "--:--";
        elements.calorieValue.textContent = "0 / 0 ккал";
        elements.proteinValue.textContent = "0%";
        elements.fatValue.textContent = "0%";
        elements.carbValue.textContent = "0%";
        elements.calorieHelp.textContent = "Выберите уровень, чтобы увидеть диапазон.";
        elements.proteinHelp.textContent = "Цель: 0%";
        elements.fatHelp.textContent = "Цель: 0%";
        elements.carbHelp.textContent = "Цель: 0%";
        [elements.calorieMeter, elements.proteinMeter, elements.fatMeter, elements.carbMeter].forEach((meter) => {
            setMeter(meter, 0, 0, 0, false, false);
        });
        elements.speedIndicator.textContent = "Скорость: 0.0";
        elements.effectIndicator.textContent = "Эффекты: нет";
        elements.scoreIndicator.textContent = "Очки: 0";
    }

    function showOverlay(eyebrow, title, body) {
        elements.overlay.classList.remove("is-hidden");
        elements.overlayCard.innerHTML = `
            <span class="game-hub-eyebrow">${escapeHtml(eyebrow)}</span>
            <h3>${escapeHtml(title)}</h3>
            <p class="mb-0">${escapeHtml(body)}</p>
        `;
    }

    function hideOverlay() {
        elements.overlay.classList.add("is-hidden");
    }

    function showResultOverlay() {
        if (!appState.latestResult || !appState.selectedLevel) {
            return;
        }

        const headline = appState.latestResult.isWin ? "Уровень пройден" : "Уровень не пройден";
        const message = appState.latestResult.isWin
            ? `Калории: ${appState.totals.calories}. Баланс: Б ${appState.percentages.protein.toFixed(1)}%, Ж ${appState.percentages.fat.toFixed(1)}%, У ${appState.percentages.carb.toFixed(1)}%.`
            : `${appState.latestResult.loseReasonLabel}. Калории: ${appState.totals.calories}. Баланс: Б ${appState.percentages.protein.toFixed(1)}%, Ж ${appState.percentages.fat.toFixed(1)}%, У ${appState.percentages.carb.toFixed(1)}%.`;
        showOverlay(headline, appState.selectedLevel.title, message);
    }

    function updateStatus(label, className) {
        elements.statusChip.textContent = label;
        elements.statusChip.className = `snake-status-chip ${className}`;
    }

    function updateActionButtons() {
        const hasLevel = Boolean(appState.selectedLevel);
        elements.retryButton.disabled = !hasLevel;

        if (!hasLevel) {
            elements.primaryActionButton.textContent = "Играть";
            elements.primaryActionButton.disabled = true;
            return;
        }

        elements.primaryActionButton.disabled = false;

        if (appState.running) {
            elements.primaryActionButton.textContent = "Игра идёт";
            elements.primaryActionButton.disabled = true;
            return;
        }

        if (appState.finished && appState.latestResult?.isWin) {
            elements.primaryActionButton.textContent = getNextLevel() ? "Следующий уровень" : "Играть снова";
            return;
        }

        elements.primaryActionButton.textContent = appState.finished ? "Начать снова" : "Играть";
    }

    function handleKeyDown(event) {
        if (event.key === "Escape") {
            const openModalNode = elements.modalBackdrops.find((modal) => !modal.classList.contains("is-hidden"));
            if (openModalNode) {
                closeModal(openModalNode.id);
            }
            return;
        }

        const direction = KEY_TO_DIRECTION[event.key];
        if (!direction || appState.activeGameTab !== "snake") {
            return;
        }

        event.preventDefault();
        queueDirection(direction);
    }

    function queueDirection(direction) {
        if (!appState.selectedLevel) {
            return;
        }

        if (!appState.running) {
            if (direction !== OPPOSITE_DIRECTION[appState.direction]) {
                appState.direction = direction;
                appState.plannedDirections = [];
                drawBoard();
            }
            return;
        }

        if (appState.effectRemainingMs > 0) {
            return;
        }

        const lastPlannedDirection = appState.plannedDirections[appState.plannedDirections.length - 1] || appState.direction;
        if (
            direction === lastPlannedDirection
            || direction === OPPOSITE_DIRECTION[lastPlannedDirection]
        ) {
            return;
        }

        appState.plannedDirections.push(direction);
    }

    function getNextDirection() {
        while (appState.plannedDirections.length) {
            const candidate = appState.plannedDirections.shift();
            if (candidate !== OPPOSITE_DIRECTION[appState.direction]) {
                return candidate;
            }
        }

        return appState.direction;
    }

    function getRandomDirection(baseDirection) {
        const candidates = Object.keys(DIRECTIONS).filter(
            (direction) => direction !== OPPOSITE_DIRECTION[baseDirection]
        );
        return candidates[randomInt(0, candidates.length - 1)];
    }

    function getRenderDirection() {
        if (appState.running && appState.effectRemainingMs <= 0 && appState.plannedDirections.length) {
            return appState.plannedDirections[0];
        }

        return appState.direction;
    }

    function getFoodCenter(food) {
        return {
            x: food.x + 0.5,
            y: food.y + 0.5,
        };
    }

    function distanceBetween(pointA, pointB) {
        return Math.hypot(pointA.x - pointB.x, pointA.y - pointB.y);
    }

    function ensureFoodPopulation() {
        if (!appState.selectedLevel) {
            return;
        }

        const healthyCodes = Object.values(appState.foodMap)
            .filter((item) => item.kind === "healthy")
            .map((item) => item.code);
        const harmfulCodes = Object.values(appState.foodMap)
            .filter((item) => item.kind === "harmful" || item.kind === "hazard")
            .map((item) => item.code);

        ["chicken", "butter", "bread"].forEach((code) => {
            if (appState.foodMap[code] && !appState.foods.some((food) => food.code === code)) {
                placeFood(code);
            }
        });

        const desiredHealthyCount = 3 + (appState.boardConfig.bonus_healthy_items || 0);
        while (
            appState.foods.filter((food) => appState.foodMap[food.code]?.kind === "healthy").length < desiredHealthyCount
        ) {
            placeFood(healthyCodes[randomInt(0, healthyCodes.length - 1)]);
        }

        while (
            appState.foods.filter((food) => appState.foodMap[food.code]?.kind !== "healthy").length < appState.desiredHarmfulCount
        ) {
            placeFood(harmfulCodes[randomInt(0, harmfulCodes.length - 1)]);
        }

        appState.foodLayerDirty = true;
    }

    function placeFood(code) {
        const freeCells = getFreeCells();
        if (!freeCells.length) {
            return;
        }

        const position = freeCells[randomInt(0, freeCells.length - 1)];
        appState.foods.push({ code, x: position.x, y: position.y });
    }

    function getFreeCells() {
        const gridSize = appState.boardConfig.grid_size;
        const occupied = new Set([
            ...appState.snake.map((segment) => `${segment.x}:${segment.y}`),
            ...appState.foods.map((food) => `${food.x}:${food.y}`),
        ]);
        const cells = [];

        for (let y = 0; y < gridSize; y += 1) {
            for (let x = 0; x < gridSize; x += 1) {
                const key = `${x}:${y}`;
                if (!occupied.has(key)) {
                    cells.push({ x, y });
                }
            }
        }

        return cells;
    }

    function hitsWall(position) {
        const gridSize = appState.boardConfig.grid_size;
        return position.x < 0 || position.y < 0 || position.x >= gridSize || position.y >= gridSize;
    }

    function calculateCurrentSpeed() {
        if (!appState.selectedLevel) {
            return 0;
        }

        const progress = Math.min(appState.totals.calories / appState.selectedLevel.target_calories, 1);
        const baseSpeed =
            (Number(appState.selectedLevel.initial_speed) * 0.94)
            + (progress * Number(appState.selectedLevel.speed_step) * 0.48);
        return Math.max(baseSpeed, 5.6);
    }

    function getCurrentStepInterval() {
        const speed = appState.currentSpeed || calculateCurrentSpeed() || 5.6;
        return 1000 / speed;
    }

    function calculateMacroPercentages() {
        const proteinCalories = appState.totals.protein * 4;
        const fatCalories = appState.totals.fat * 9;
        const carbCalories = appState.totals.carb * 4;
        const totalMacroCalories = proteinCalories + fatCalories + carbCalories;

        if (!totalMacroCalories) {
            return { protein: 0, fat: 0, carb: 0 };
        }

        return {
            protein: roundToTwo((proteinCalories / totalMacroCalories) * 100),
            fat: roundToTwo((fatCalories / totalMacroCalories) * 100),
            carb: roundToTwo((carbCalories / totalMacroCalories) * 100),
        };
    }

    function isWinState() {
        if (!appState.selectedLevel) {
            return false;
        }

        return (
            isBetween(appState.totals.calories, appState.selectedLevel.min_calories, appState.selectedLevel.max_calories)
            && isBetween(appState.percentages.protein, appState.selectedLevel.min_protein_percent, appState.selectedLevel.max_protein_percent)
            && isBetween(appState.percentages.fat, appState.selectedLevel.min_fat_percent, appState.selectedLevel.max_fat_percent)
            && isBetween(appState.percentages.carb, appState.selectedLevel.min_carb_percent, appState.selectedLevel.max_carb_percent)
        );
    }

    function estimateScore(isWin) {
        if (!appState.selectedLevel) {
            return 0;
        }

        const calorieWindow = Math.max(appState.selectedLevel.max_calories - appState.selectedLevel.min_calories, 1);
        const calorieAccuracy = Math.max(
            0,
            1 - Math.abs(appState.totals.calories - appState.selectedLevel.target_calories) / calorieWindow
        );
        const macroDeviation = (
            Math.abs(appState.percentages.protein - appState.selectedLevel.target_protein_percent)
            + Math.abs(appState.percentages.fat - appState.selectedLevel.target_fat_percent)
            + Math.abs(appState.percentages.carb - appState.selectedLevel.target_carb_percent)
        ) / 3;
        const macroAccuracy = Math.max(0, 1 - (macroDeviation / 25));
        const timeRatio = appState.selectedLevel.time_limit_seconds
            ? Math.max(0, appState.timerRemainingMs / 1000) / appState.selectedLevel.time_limit_seconds
            : 0;

        if (isWin) {
            return Math.round((calorieAccuracy * 60) + (macroAccuracy * 25) + (timeRatio * 15));
        }

        const progress = Math.min(appState.totals.calories / appState.selectedLevel.target_calories, 1);
        return Math.round((progress * 40) + (macroAccuracy * 20));
    }

    function setMeter(meterElement, fillWidth, targetStart, targetWidth, isPerfect, isDanger) {
        meterElement.style.setProperty("--fill-width", `${Math.max(0, Math.min(fillWidth, 100))}%`);
        meterElement.style.setProperty("--target-start", `${Math.max(0, Math.min(targetStart, 100))}%`);
        meterElement.style.setProperty("--target-width", `${Math.max(0, Math.min(targetWidth, 100))}%`);
        meterElement.classList.toggle("is-perfect", Boolean(isPerfect));
        meterElement.classList.toggle("is-danger", Boolean(isDanger));
    }

    function prepareCanvas() {
        if (!appState.canvasSizeDirty) {
            return;
        }

        const dpr = Math.min(window.devicePixelRatio || 1, MAX_CANVAS_DPR);
        const shellWidth = elements.boardShell?.clientWidth || 0;
        const shellHeight = elements.boardShell?.clientHeight || 0;
        const preferredSize = appState.boardConfig
            ? appState.boardConfig.grid_size * (appState.boardConfig.cell_size || 30)
            : 600;
        let cssSize = preferredSize;

        if (shellWidth > 0 && shellHeight > 0) {
            cssSize = Math.min(preferredSize, Math.floor(Math.min(shellWidth - 12, shellHeight - 12)));
        } else {
            cssSize = Math.min(
                preferredSize,
                Math.floor(Math.min(window.innerWidth - 24, window.innerHeight - 180))
            );
        }

        cssSize = Math.max(cssSize, 120);
        if (cssSize === appState.canvasSize && dpr === appState.canvasDpr) {
            appState.canvasSizeDirty = false;
            return;
        }

        appState.canvasSize = cssSize;
        appState.canvasDpr = dpr;
        appState.canvasSizeDirty = false;
        appState.boardLayoutDirty = true;
        appState.foodLayerDirty = true;
        appState.boardBackgroundCanvas = null;
        appState.boardBackgroundSignature = "";
        elements.canvas.style.width = `${cssSize}px`;
        elements.canvas.style.height = `${cssSize}px`;
        elements.canvas.width = Math.round(cssSize * dpr);
        elements.canvas.height = Math.round(cssSize * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function drawEmptyBoard() {
        prepareCanvas();
        ctx.clearRect(0, 0, appState.canvasSize, appState.canvasSize);
        drawBoardBackground(20);
    }

    function drawBoard() {
        if (!appState.boardConfig) {
            drawEmptyBoard();
            return;
        }

        prepareCanvas();

        const gridSize = appState.boardConfig.grid_size;
        const cellSize = appState.canvasSize / gridSize;
        const stepInterval = appState.currentSpeed > 0 ? getCurrentStepInterval() : 1000;
        const progress = appState.running && ENABLE_SNAKE_INTERPOLATION
            ? Math.min(appState.moveAccumulatorMs / stepInterval, 1)
            : 0;
        ctx.clearRect(0, 0, appState.canvasSize, appState.canvasSize);
        drawBoardBackground(gridSize);
        drawFoods(cellSize);
        drawSnake(getSnakeRenderPath(progress, cellSize), cellSize);

        if (appState.effectRemainingMs > 0) {
            ctx.fillStyle = "rgba(92, 145, 255, 0.14)";
            ctx.fillRect(0, 0, appState.canvasSize, appState.canvasSize);
        }
    }

    function drawBoardBackground(gridSize) {
        const cellSize = appState.canvasSize / gridSize;
        ctx.fillStyle = "#aad751";
        ctx.fillRect(0, 0, appState.canvasSize, appState.canvasSize);

        ctx.fillStyle = "#a2d149";
        for (let y = 0; y < gridSize; y += 1) {
            for (let x = 0; x < gridSize; x += 1) {
                if ((x + y) % 2 === 0) {
                    ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                }
            }
        }
    }

    function drawFoods(cellSize) {
        if (!appState.foods.length) {
            return;
        }

        appState.foods.forEach((food) => {
            const foodData = appState.foodMap[food.code];
            if (!foodData) {
                return;
            }

            const sprite = getFoodSprite(foodData, cellSize);
            if (!sprite) {
                return;
            }

            ctx.drawImage(sprite, food.x * cellSize, food.y * cellSize, cellSize, cellSize);
        });
    }

    function getFoodSprite(foodData, cellSize) {
        const spriteSize = Math.max(Math.round(cellSize), 1);
        const cacheKey = `${foodData.code}:${spriteSize}`;
        if (appState.foodSpriteCache[cacheKey]) {
            return appState.foodSpriteCache[cacheKey];
        }

        const spriteCanvas = document.createElement("canvas");
        spriteCanvas.width = spriteSize;
        spriteCanvas.height = spriteSize;
        const spriteCtx = spriteCanvas.getContext("2d");
        if (!spriteCtx) {
            return null;
        }

        spriteCtx.textAlign = "center";
        spriteCtx.textBaseline = "middle";
        spriteCtx.font = `${Math.floor(spriteSize * 0.84)}px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif`;
        spriteCtx.fillText(foodData.emoji || "?", spriteSize / 2, (spriteSize / 2) + (spriteSize * 0.02));

        appState.foodSpriteCache[cacheKey] = spriteCanvas;
        return spriteCanvas;
    }

    function getSnakeRenderPath(progress, cellSize) {
        if (!appState.snake.length) {
            return [];
        }

        const isDead = appState.finished && !appState.latestResult?.isWin;
        const headVector = DIRECTIONS[appState.direction] || DIRECTIONS.right;
        const head = appState.snake[0];
        const points = [
            {
                x: (head.x + 0.5 + (headVector.x * progress)) * cellSize,
                y: (head.y + 0.5 + (headVector.y * progress)) * cellSize,
            },
        ];

        for (let index = 0; index < appState.snake.length - 1; index += 1) {
            const segment = appState.snake[index];
            points.push({
                x: (segment.x + 0.5) * cellSize,
                y: (segment.y + 0.5) * cellSize,
            });
        }

        if (appState.snake.length > 1) {
            const tail = appState.snake[appState.snake.length - 1];
            const preTail = appState.snake[appState.snake.length - 2];
            points.push({
                x: (tail.x + 0.5 + ((appState.grewLastStep || isDead) ? 0 : ((preTail.x - tail.x) * progress))) * cellSize,
                y: (tail.y + 0.5 + ((appState.grewLastStep || isDead) ? 0 : ((preTail.y - tail.y) * progress))) * cellSize,
            });
        }

        return points;
    }

    function drawSnake(points, cellSize) {
        if (!points.length) {
            return;
        }

        const isDead = appState.finished && !appState.latestResult?.isWin;
        const bodyWidth = cellSize * 0.75;
        const headPoint = points[0];
        const faceDirection = DIRECTIONS[getRenderDirection()] || DIRECTIONS.right;

        ctx.save();
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.strokeStyle = isDead ? "#8e44ad" : "#4e7cf6";
        ctx.lineWidth = bodyWidth;
        ctx.beginPath();
        ctx.moveTo(headPoint.x, headPoint.y);

        for (let index = 1; index < points.length; index += 1) {
            ctx.lineTo(points[index].x, points[index].y);
        }

        ctx.stroke();
        drawSnakeFace(headPoint.x, headPoint.y, faceDirection, isDead, cellSize);
        ctx.restore();
    }

    function drawSnakeFace(centerX, centerY, vector, isDead, cellSize) {
        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(Math.atan2(vector.y, vector.x));

        const headSize = cellSize * 0.85;
        ctx.fillStyle = isDead ? "#8e44ad" : "#4e7cf6";
        fillRoundedRect(ctx, -headSize / 2, -headSize / 2, headSize, headSize, cellSize * 0.28);

        const closestFood = getClosestFoodPixel();
        if (closestFood && !isDead) {
            const distToFood = Math.hypot(centerX - closestFood.x, centerY - closestFood.y);
            if (distToFood < cellSize * 2.5) {
                ctx.fillStyle = "#ff4d4d";
                ctx.fillRect(cellSize * 0.33, -cellSize * 0.07, cellSize * 0.4, cellSize * 0.14);
                ctx.fillRect(cellSize * 0.66, -cellSize * 0.16, cellSize * 0.1, cellSize * 0.1);
                ctx.fillRect(cellSize * 0.66, cellSize * 0.06, cellSize * 0.1, cellSize * 0.1);
            }
        }

        if (isDead) {
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = Math.max(2, cellSize * 0.06);
            drawX(ctx, cellSize * 0.1, -cellSize * 0.2, cellSize * 0.1);
            drawX(ctx, cellSize * 0.1, cellSize * 0.2, cellSize * 0.1);
        } else {
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(cellSize * 0.13, -cellSize * 0.2, cellSize * 0.16, 0, Math.PI * 2);
            ctx.arc(cellSize * 0.13, cellSize * 0.2, cellSize * 0.16, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#000000";
            ctx.beginPath();
            ctx.arc(cellSize * 0.2, -cellSize * 0.2, cellSize * 0.08, 0, Math.PI * 2);
            ctx.arc(cellSize * 0.2, cellSize * 0.2, cellSize * 0.08, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }

    function fillRoundedRect(targetCtx, x, y, width, height, radius) {
        targetCtx.beginPath();
        targetCtx.moveTo(x + radius, y);
        targetCtx.lineTo(x + width - radius, y);
        targetCtx.quadraticCurveTo(x + width, y, x + width, y + radius);
        targetCtx.lineTo(x + width, y + height - radius);
        targetCtx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        targetCtx.lineTo(x + radius, y + height);
        targetCtx.quadraticCurveTo(x, y + height, x, y + height - radius);
        targetCtx.lineTo(x, y + radius);
        targetCtx.quadraticCurveTo(x, y, x + radius, y);
        targetCtx.closePath();
        targetCtx.fill();
    }

    function drawX(targetCtx, x, y, size) {
        targetCtx.beginPath();
        targetCtx.moveTo(x - size, y - size);
        targetCtx.lineTo(x + size, y + size);
        targetCtx.moveTo(x + size, y - size);
        targetCtx.lineTo(x - size, y + size);
        targetCtx.stroke();
    }

    function getClosestFoodPixel() {
        if (!appState.foods.length || !appState.boardConfig) {
            return null;
        }

        const cellSize = appState.canvasSize / appState.boardConfig.grid_size;
        const head = appState.snake[0];
        let closestFood = null;
        let closestDistance = Number.POSITIVE_INFINITY;

        appState.foods.forEach((food) => {
            const distance = Math.hypot(food.x - head.x, food.y - head.y);
            if (distance < closestDistance) {
                closestDistance = distance;
                closestFood = {
                    x: (food.x * cellSize) + (cellSize / 2),
                    y: (food.y * cellSize) + (cellSize / 2),
                };
            }
        });

        return closestFood;
    }

    function getNextLevel() {
        const currentIndex = appState.levels.findIndex((level) => level.id === appState.selectedLevelId);
        if (currentIndex === -1 || currentIndex >= appState.levels.length - 1) {
            return null;
        }
        return appState.levels[currentIndex + 1];
    }

    function formatTime(totalSeconds) {
        const secondsValue = Math.max(0, Number(totalSeconds) || 0);
        const minutes = String(Math.floor(secondsValue / 60)).padStart(2, "0");
        const seconds = String(secondsValue % 60).padStart(2, "0");
        return `${minutes}:${seconds}`;
    }

    function formatDateTime(value) {
        const date = new Date(value);
        return date.toLocaleString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function getCookie(name) {
        const cookieString = document.cookie || "";
        const cookie = cookieString
            .split(";")
            .map((entry) => entry.trim())
            .find((entry) => entry.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
    }

    function isBetween(value, min, max) {
        return value >= min && value <= max;
    }

    function roundToTwo(value) {
        return Math.round(value * 100) / 100;
    }

    function randomInt(min, max) {
        if (max < min) {
            return min;
        }
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }
})();
