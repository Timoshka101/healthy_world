(() => {
    const configNode = document.getElementById("snake-frontend-config");
    const modal = document.getElementById("vitamin-game-modal");
    const openButton = document.getElementById("vitamin-open-btn");
    const selectorModal = document.getElementById("vitamin-selector-modal");
    const selectorOpenButton = document.getElementById("vitamin-open-selector-btn");

    if (!configNode || !modal || !openButton || !selectorModal || !selectorOpenButton) {
        return;
    }

    const frontendConfig = JSON.parse(configNode.textContent);

    const elements = {
        modal,
        openButton,
        selectorModal,
        selectorOpenButton,
        closeButtons: Array.from(document.querySelectorAll('[data-close-modal="vitamin-game-modal"]')),
        selectorCloseButtons: Array.from(document.querySelectorAll('[data-close-modal="vitamin-selector-modal"]')),
        avatar: document.getElementById("vitamin-avatar"),
        avatarFace: document.getElementById("vitamin-avatar-face"),
        statusTitle: document.getElementById("vitamin-status-title"),
        statusText: document.getElementById("vitamin-status-text"),
        timerDisplay: document.getElementById("vitamin-timer-display"),
        normalZoneDisplay: document.getElementById("vitamin-normal-zone-display"),
        selector: document.getElementById("vitamin-selector"),
        selectionNote: document.getElementById("vitamin-selection-note"),
        selectedSummary: document.getElementById("vitamin-selected-summary"),
        bars: document.getElementById("vitamin-bars"),
        products: document.getElementById("vitamin-products"),
        resultBox: document.getElementById("vitamin-result-box"),
        saveNote: document.getElementById("vitamin-save-note"),
        startButton: document.getElementById("vitamin-start-btn"),
        restartButton: document.getElementById("vitamin-restart-btn"),
    };

    const state = {
        level: null,
        vitamins: [],
        products: [],
        selectedVitaminCodes: [],
        values: {},
        running: false,
        finished: false,
        isWin: false,
        loseReason: "",
        timeRemainingMs: 0,
        frameId: null,
        lastFrameTime: 0,
        startedAtIso: "",
        configLoaded: false,
        configLoading: false,
        saveState: "idle",
        selectionWarning: false,
    };

    const LOSE_REASON_TEXT = {
        vitamin_a_low: "Слишком низкий витамин A. Это авитаминоз.",
        vitamin_b_low: "Слишком низкий витамин B. Это авитаминоз.",
        vitamin_c_low: "Слишком низкий витамин C. Это авитаминоз.",
        vitamin_d_low: "Слишком низкий витамин D. Это авитаминоз.",
        vitamin_e_low: "Слишком низкий витамин E. Это авитаминоз.",
        vitamin_k_low: "Слишком низкий витамин K. Это авитаминоз.",
        vitamin_a_high: "Витамин A стал слишком высоким. Это гипервитаминоз.",
        vitamin_b_high: "Витамин B стал слишком высоким. Это гипервитаминоз.",
        vitamin_c_high: "Витамин C стал слишком высоким. Это гипервитаминоз.",
        vitamin_d_high: "Витамин D стал слишком высоким. Это гипервитаминоз.",
        vitamin_e_high: "Витамин E стал слишком высоким. Это гипервитаминоз.",
        vitamin_k_high: "Витамин K стал слишком высоким. Это гипервитаминоз.",
    };

    bindEvents();
    updateStaticView();
    renderGame();
    ensureConfigLoaded();

    function bindEvents() {
        openButton.addEventListener("click", async () => {
            await ensureConfigLoaded();
            if (!state.level) {
                return;
            }
            if (!hasValidSelection()) {
                state.selectionWarning = true;
                openSelectorModal();
                renderGame();
                return;
            }
            openModal();
        });

        selectorOpenButton.addEventListener("click", async () => {
            await ensureConfigLoaded();
            if (!state.level) {
                return;
            }
            openSelectorModal();
        });

        elements.startButton.addEventListener("click", async () => {
            await ensureConfigLoaded();
            if (!hasValidSelection()) {
                state.selectionWarning = true;
                renderGame();
                return;
            }
            startGame();
        });

        elements.restartButton.addEventListener("click", async () => {
            await ensureConfigLoaded();
            if (!state.level) {
                return;
            }
            if (hasValidSelection()) {
                startGame();
                return;
            }
            state.selectionWarning = true;
            resetPreview();
        });

        elements.selector.addEventListener("click", (event) => {
            const button = event.target.closest("[data-vitamin-code]");
            if (!button || state.running) {
                return;
            }

            toggleVitaminSelection(button.dataset.vitaminCode);
        });

        elements.products.addEventListener("click", (event) => {
            const button = event.target.closest("[data-vitamin-product]");
            if (!button || !state.running || state.finished) {
                return;
            }

            const product = state.products.find((item) => item.code === button.dataset.vitaminProduct);
            if (!product) {
                return;
            }

            applyProduct(product);
        });

        elements.closeButtons.forEach((button) => {
            button.addEventListener("click", closeModal);
        });

        elements.selectorCloseButtons.forEach((button) => {
            button.addEventListener("click", closeSelectorModal);
        });

        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });

        selectorModal.addEventListener("click", (event) => {
            if (event.target === selectorModal) {
                closeSelectorModal();
            }
        });
    }

    async function ensureConfigLoaded() {
        if (state.configLoaded || state.configLoading) {
            return;
        }

        state.configLoading = true;
        elements.resultBox.textContent = "Загружаю параметры игры...";

        try {
            const response = await fetch(frontendConfig.api.vitamin_config, {
                headers: { Accept: "application/json" },
            });

            if (!response.ok) {
                throw new Error("Не удалось загрузить параметры игры.");
            }

            const payload = await response.json();
            state.level = payload.level;
            state.vitamins = Array.isArray(payload.level?.vitamins) ? payload.level.vitamins : [];
            state.products = Array.isArray(payload.level?.products) ? payload.level.products : [];
            state.selectedVitaminCodes = getInitialSelection();
            state.configLoaded = true;
            updateStaticView();
            resetPreview();
        } catch (error) {
            elements.resultBox.textContent = "Не удалось загрузить игру. Обновите страницу и попробуйте снова.";
        } finally {
            state.configLoading = false;
        }
    }

    function updateStaticView() {
        if (!state.level) {
            return;
        }

        elements.normalZoneDisplay.textContent = `${state.level.normal_min_value}–${state.level.normal_max_value}`;
    }

    function getInitialSelection() {
        const selectionSize = getSelectionSize();
        const fallback = Array.isArray(state.level?.default_selected_vitamins)
            ? state.level.default_selected_vitamins
            : [];
        const validFallback = fallback.filter((code) => getVitaminMeta(code));
        const selected = [];

        validFallback.forEach((code) => {
            if (!selected.includes(code) && selected.length < selectionSize) {
                selected.push(code);
            }
        });

        state.vitamins.forEach((vitamin) => {
            if (!selected.includes(vitamin.code) && selected.length < selectionSize) {
                selected.push(vitamin.code);
            }
        });

        return selected;
    }

    function openModal() {
        modal.classList.remove("is-hidden");
        document.body.classList.add("game-modal-open");
        renderGame();
    }

    function openSelectorModal() {
        selectorModal.classList.remove("is-hidden");
        document.body.classList.add("game-modal-open");
        renderGame();
    }

    function closeModal() {
        stopLoop();
        modal.classList.add("is-hidden");
        syncBodyLock();
        resetPreview();
    }

    function closeSelectorModal() {
        selectorModal.classList.add("is-hidden");
        syncBodyLock();
        renderGame();
    }

    function syncBodyLock() {
        const hasOpenModal = Array.from(document.querySelectorAll(".snake-modal-backdrop")).some(
            (backdrop) => !backdrop.classList.contains("is-hidden"),
        );
        document.body.classList.toggle("game-modal-open", hasOpenModal);
    }

    function resetPreview() {
        if (!state.level) {
            return;
        }

        state.values = {};
        state.vitamins.forEach((vitamin) => {
            state.values[vitamin.code] = state.level.start_value;
        });

        state.timeRemainingMs = state.level.time_limit_seconds * 1000;
        state.running = false;
        state.finished = false;
        state.isWin = false;
        state.loseReason = "";
        state.startedAtIso = "";
        state.saveState = frontendConfig.user.is_authenticated ? "idle" : "guest";
        renderGame();
    }

    function startGame() {
        if (!state.level || !hasValidSelection()) {
            return;
        }

        state.selectionWarning = false;
        resetPreview();
        state.running = true;
        state.startedAtIso = new Date().toISOString();
        state.lastFrameTime = performance.now();
        renderGame();
        stopLoop();
        state.frameId = requestAnimationFrame(gameLoop);
    }

    function stopLoop() {
        if (state.frameId) {
            cancelAnimationFrame(state.frameId);
            state.frameId = null;
        }
    }

    function gameLoop(now) {
        if (!state.running || state.finished || !state.level) {
            state.frameId = null;
            return;
        }

        const deltaMs = Math.min(now - state.lastFrameTime, 120);
        state.lastFrameTime = now;
        const effectiveDeltaMs = Math.min(deltaMs, state.timeRemainingMs);
        const drainAmount = state.level.drain_per_second * (effectiveDeltaMs / 1000);

        state.selectedVitaminCodes.forEach((vitaminCode) => {
            state.values[vitaminCode] = clampValue(state.values[vitaminCode] - drainAmount);
        });

        state.timeRemainingMs = Math.max(0, state.timeRemainingMs - effectiveDeltaMs);

        const loseReason = getCriticalReason();
        if (loseReason) {
            finishGame(false, loseReason);
            return;
        }

        if (state.timeRemainingMs <= 0) {
            finishGame(true, "");
            return;
        }

        renderGame();
        state.frameId = requestAnimationFrame(gameLoop);
    }

    function applyProduct(product) {
        if (!product?.vitamin_code) {
            return;
        }

        state.values[product.vitamin_code] = clampValue(
            state.values[product.vitamin_code] + product.boost,
        );

        const loseReason = getCriticalReason();
        if (loseReason) {
            finishGame(false, loseReason);
            return;
        }

        renderGame();
    }

    function finishGame(isWin, loseReason) {
        state.running = false;
        state.finished = true;
        state.isWin = isWin;
        state.loseReason = loseReason;
        stopLoop();
        renderGame();
        saveResult();
    }

    async function saveResult() {
        if (!frontendConfig.user.is_authenticated || !state.level) {
            state.saveState = "guest";
            renderSaveNote();
            return;
        }

        state.saveState = "saving";
        renderSaveNote();

        try {
            const body = {
                level_id: state.level.id,
                is_win: state.isWin,
                lose_reason: state.loseReason,
                selected_vitamins: state.selectedVitaminCodes,
                duration_seconds: getDurationSeconds(),
                started_at: state.startedAtIso,
            };

            state.vitamins.forEach((vitamin) => {
                body[vitamin.code] = roundValue(state.values[vitamin.code] ?? 0);
            });

            const response = await fetch(frontendConfig.api.vitamin_result, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    Accept: "application/json",
                },
                body: JSON.stringify(body),
            });

            state.saveState = response.ok ? "saved" : "error";
        } catch (error) {
            state.saveState = "error";
        }

        renderSaveNote();
    }

    function toggleVitaminSelection(vitaminCode) {
        const selectionSize = getSelectionSize();

        if (state.selectedVitaminCodes.includes(vitaminCode)) {
            state.selectedVitaminCodes = state.selectedVitaminCodes.filter((code) => code !== vitaminCode);
        } else if (state.selectedVitaminCodes.length < selectionSize) {
            state.selectedVitaminCodes = [...state.selectedVitaminCodes, vitaminCode];
        } else {
            state.selectionWarning = true;
            renderGame();
            return;
        }

        state.selectionWarning = false;
        resetPreview();
    }

    function getCriticalReason() {
        if (!state.level) {
            return "";
        }

        for (const vitaminCode of state.selectedVitaminCodes) {
            if ((state.values[vitaminCode] ?? 0) < state.level.min_critical_value) {
                return `${vitaminCode}_low`;
            }
        }

        for (const vitaminCode of state.selectedVitaminCodes) {
            if ((state.values[vitaminCode] ?? 0) > state.level.max_critical_value) {
                return `${vitaminCode}_high`;
            }
        }

        return "";
    }

    function renderGame() {
        if (!state.level) {
            return;
        }

        renderStaticCollections();
        renderSelectedSummary();
        renderBars();

        elements.timerDisplay.textContent = formatTimer(state.timeRemainingMs);
        renderStatus();
        renderButtons();
        renderSelectionNote();
        renderSaveNote();
    }

    function renderStaticCollections() {
        const selectionKey = state.selectedVitaminCodes.join("|");
        const selectorSignature = `${selectionKey}:${state.running ? "1" : "0"}`;

        if (elements.selector.dataset.renderSignature !== selectorSignature) {
            renderVitaminSelector();
            elements.selector.dataset.renderSignature = selectorSignature;
        }

        if (elements.products.dataset.renderSignature !== selectionKey) {
            renderProducts();
            elements.products.dataset.renderSignature = selectionKey;
        }
    }

    function renderVitaminSelector() {
        const selectedSet = new Set(state.selectedVitaminCodes);
        elements.selector.innerHTML = state.vitamins
            .map((vitamin) => `
                <button
                    type="button"
                    class="vitamin-pick-button${selectedSet.has(vitamin.code) ? " is-selected" : ""}"
                    data-vitamin-code="${vitamin.code}"
                    ${state.running ? "disabled" : ""}
                >
                    <span class="vitamin-pick-name">${vitamin.display_name}</span>
                    <span class="vitamin-pick-meta">${vitamin.label}</span>
                </button>
            `)
            .join("");
    }

    function renderBars() {
        const selectionSize = getSelectionSize();
        const selected = state.selectedVitaminCodes.slice(0, selectionSize);
        const safeWidth = Math.max(state.level.normal_max_value - state.level.normal_min_value, 0);

        elements.bars.innerHTML = selected
            .map((vitaminCode) => {
                const vitamin = getVitaminMeta(vitaminCode);
                return `
                    <article class="vitamin-bar-card">
                        <span class="vitamin-bar-label">${vitamin?.label || vitaminCode}</span>
                        <div
                            class="vitamin-bar-track"
                            data-vitamin-track="${vitaminCode}"
                            style="--safe-start: ${state.level.normal_min_value}%; --safe-width: ${safeWidth}%"
                        >
                            <div class="vitamin-bar-safe-zone"></div>
                            <div class="vitamin-bar-fill"></div>
                        </div>
                        <strong class="vitamin-bar-readout" data-vitamin-value="${vitaminCode}">0 / 100</strong>
                    </article>
                `;
            })
            .join("");

        selected.forEach((vitaminCode) => {
            const bar = elements.bars.querySelector(`[data-vitamin-track="${vitaminCode}"]`);
            const valueNode = elements.bars.querySelector(`[data-vitamin-value="${vitaminCode}"]`);
            renderBar(bar, valueNode, state.values[vitaminCode] ?? 0);
        });
    }

    function renderSelectedSummary() {
        if (!elements.selectedSummary) {
            return;
        }

        const selected = state.selectedVitaminCodes
            .map((vitaminCode) => {
                const vitamin = getVitaminMeta(vitaminCode);
                return vitamin ? `${vitamin.short_label} ${state.level.start_value}` : vitaminCode;
            });

        elements.selectedSummary.textContent = selected.join(" / ");
    }

    function renderProducts() {
        const selectedSet = new Set(state.selectedVitaminCodes);
        const visibleProducts = state.products.filter((product) => selectedSet.has(product.vitamin_code));

        if (!visibleProducts.length) {
            elements.products.innerHTML = `
                <div class="vitamin-product-placeholder">
                    Выберите три витамина, и здесь появятся подходящие продукты.
                </div>
            `;
            return;
        }

        elements.products.innerHTML = visibleProducts
            .map((product) => `
                <button
                    type="button"
                    class="vitamin-product-button${product.strength === "strong" ? " is-strong" : ""}"
                    data-vitamin-product="${product.code}"
                >
                    <span class="vitamin-product-emoji">${product.emoji}</span>
                    <span class="vitamin-product-name">${product.label}</span>
                    <span class="vitamin-product-boost">${product.vitamin_short_label} +${product.boost}</span>
                </button>
            `)
            .join("");
    }

    function renderBar(bar, valueNode, value) {
        if (!bar || !valueNode) {
            return;
        }

        const safe = value >= state.level.normal_min_value && value <= state.level.normal_max_value;
        const danger = value < state.level.min_critical_value || value > state.level.max_critical_value;
        const warningBand = 6;
        const nearBorder = safe && (
            value - state.level.normal_min_value <= warningBand
            || state.level.normal_max_value - value <= warningBand
        );
        const warning = (!safe && !danger) || nearBorder;
        const ok = safe && !nearBorder;

        bar.style.setProperty("--fill-width", `${Math.max(0, Math.min(100, value))}%`);
        bar.classList.toggle("is-danger", danger);
        bar.classList.toggle("is-warning", warning);
        bar.classList.toggle("is-ok", ok);
        valueNode.textContent = `${roundValue(value)} / 100`;
    }

    function renderStatus() {
        let face = "🙂";
        let title = "Баланс спокоен";
        let text = "Выберите три витамина и держите их в безопасной зоне.";
        let stateClass = "is-good";

        if (!hasValidSelection()) {
            face = "🤔";
            title = "Нужно выбрать витамины";
            text = `Перед стартом выберите ровно ${getSelectionSize()} витамина для этого раунда.`;
            stateClass = "is-warning";
            elements.resultBox.textContent = "Сначала выберите три витамина, с которыми будете играть.";
        } else if (state.finished && state.isWin) {
            face = "😄";
            title = "Победа";
            text = "Вы продержались до конца таймера и сохранили баланс выбранных витаминов.";
            stateClass = "is-win";
            elements.resultBox.textContent = "Победа! Выбранные витамины остались в безопасной зоне до конца игры.";
        } else if (state.finished) {
            face = "😵";
            title = "Поражение";
            text = LOSE_REASON_TEXT[state.loseReason] || "Баланс витаминов вышел за критические пределы.";
            stateClass = "is-danger";
            elements.resultBox.textContent = text;
        } else if (state.running) {
            const criticalReason = getCriticalReason();
            const inNormalZone = isInNormalZone();

            if (criticalReason) {
                face = "😵";
                title = "Критическое состояние";
                text = LOSE_REASON_TEXT[criticalReason] || "Нужно срочно восстановить баланс.";
                stateClass = "is-danger";
            } else if (inNormalZone) {
                face = "🙂";
                title = "Баланс в норме";
                text = "Так держать: все выбранные витамины сейчас в безопасной зоне.";
                stateClass = "is-good";
            } else {
                face = "😬";
                title = "Нужна корректировка";
                text = "Один из выбранных витаминов уходит от нормы. Подберите нужный продукт.";
                stateClass = "is-warning";
            }

            elements.resultBox.textContent = "Игра идёт: следите за выбранными витаминами и реагируйте вовремя.";
        } else {
            elements.resultBox.textContent = "Нажмите «Старт», когда выберете три витамина для раунда.";
        }

        elements.avatar.className = `vitamin-avatar ${stateClass}`;
        elements.avatarFace.textContent = face;
        elements.statusTitle.textContent = title;
        elements.statusText.textContent = text;
    }

    function renderButtons() {
        const disableProducts = !state.running || state.finished;
        elements.products.querySelectorAll(".vitamin-product-button").forEach((button) => {
            button.disabled = disableProducts;
        });

        elements.startButton.disabled = state.running || !hasValidSelection();
        elements.restartButton.disabled = state.running || !hasValidSelection();
    }

    function renderSelectionNote() {
        const selectedCount = state.selectedVitaminCodes.length;
        const selectionSize = getSelectionSize();

        if (state.selectionWarning && selectedCount !== selectionSize) {
            elements.selectionNote.textContent = `Нужно выбрать ровно ${selectionSize} витамина. Сейчас выбрано: ${selectedCount}.`;
            elements.selectionNote.classList.add("is-warning");
            return;
        }

        if (selectedCount < selectionSize) {
            elements.selectionNote.textContent = `Выберите ещё ${selectionSize - selectedCount} витамина.`;
            elements.selectionNote.classList.remove("is-warning");
            return;
        }

        elements.selectionNote.textContent = "Выбрано 3 витамина. Можно начинать игру.";
        elements.selectionNote.classList.remove("is-warning");
    }

    function renderSaveNote() {
        if (!frontendConfig.user.is_authenticated) {
            elements.saveNote.textContent = "Играть можно без входа, но результаты сохраняются только для авторизованных пользователей.";
            return;
        }

        if (state.saveState === "saving") {
            elements.saveNote.textContent = "Сохраняю результат...";
            return;
        }

        if (state.saveState === "saved") {
            elements.saveNote.textContent = "Результат сохранён в статистике.";
            return;
        }

        if (state.saveState === "error") {
            elements.saveNote.textContent = "Не удалось сохранить результат. Сама игра при этом завершилась нормально.";
            return;
        }

        elements.saveNote.textContent = "Результат сохранится в статистике после завершения.";
    }

    function isInNormalZone() {
        return state.selectedVitaminCodes.every((vitaminCode) => {
            const value = state.values[vitaminCode] ?? 0;
            return value >= state.level.normal_min_value && value <= state.level.normal_max_value;
        });
    }

    function getVitaminMeta(code) {
        return state.vitamins.find((vitamin) => vitamin.code === code) || null;
    }

    function hasValidSelection() {
        return state.selectedVitaminCodes.length === getSelectionSize();
    }

    function getSelectionSize() {
        return Number(state.level?.selection_size) || 3;
    }

    function getDurationSeconds() {
        if (!state.level) {
            return 0;
        }
        return Math.max(
            0,
            Math.round((state.level.time_limit_seconds * 1000 - state.timeRemainingMs) / 1000),
        );
    }

    function formatTimer(timeRemainingMs) {
        const totalSeconds = Math.max(0, Math.ceil(timeRemainingMs / 1000));
        const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const seconds = String(totalSeconds % 60).padStart(2, "0");
        return `${minutes}:${seconds}`;
    }

    function clampValue(value) {
        return Math.max(0, Math.min(100, value));
    }

    function roundValue(value) {
        return Math.round(value * 10) / 10;
    }

    function getCookie(name) {
        const cookieValue = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));

        if (!cookieValue) {
            return "";
        }

        return decodeURIComponent(cookieValue.split("=").slice(1).join("="));
    }
})();
