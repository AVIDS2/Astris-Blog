<script>
import { onMount, onDestroy } from "svelte";
import { pioConfig } from "@/config";

let canvas;
let app = null;
let model = null;
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;
let positionX = 0;
let positionY = 0;

// === 对话气泡 & 交互状态 ===
let currentDialog = "";
let showDialog = false;
let dialogTimer = null;
let idleTimer = null;
let isWidgetVisible = true;
let isMobile = false;

const DIALOG_DURATION = 4000;
const IDLE_INTERVAL = 30000;

const modelPath = pioConfig.models?.[0] || "/pio/models/whitecat/sdwhite cat free.model3.json";

// === 工具函数 ===

function randomPick(arr) {
    if (!arr || arr.length === 0) return "";
    return arr[Math.floor(Math.random() * arr.length)];
}

function displayDialog(text) {
    if (!text) return;
    currentDialog = text;
    showDialog = true;
    if (dialogTimer) clearTimeout(dialogTimer);
    dialogTimer = setTimeout(() => {
        showDialog = false;
        currentDialog = "";
    }, DIALOG_DURATION);
}

function getTimeGreeting() {
    const tg = pioConfig.dialog?.timeGreetings;
    if (!tg) return "";
    const hour = new Date().getHours();
    if (hour >= 6 && hour < 11) return randomPick(tg.morning);
    if (hour >= 11 && hour < 14) return randomPick(tg.noon);
    if (hour >= 14 && hour < 18) return randomPick(tg.afternoon);
    if (hour >= 18 && hour < 23) return randomPick(tg.evening);
    return randomPick(tg.lateNight);
}

function resetIdleTimer() {
    if (idleTimer) clearTimeout(idleTimer);
    const idleMessages = pioConfig.dialog?.idle;
    if (!idleMessages || idleMessages.length === 0) return;
    idleTimer = setTimeout(() => {
        if (isWidgetVisible) {
            displayDialog(randomPick(idleMessages));
        }
        resetIdleTimer();
    }, IDLE_INTERVAL);
}

/** 收起/展开猫娘 - 用 CSS 控制，不销毁 DOM */
function toggleWidget() {
    isWidgetVisible = !isWidgetVisible;
    if (isWidgetVisible) {
        // 展开时显示欢迎
        const timeGreeting = getTimeGreeting();
        if (timeGreeting) {
            setTimeout(() => displayDialog(timeGreeting), 300);
        }
    }
}

function handleContainerClick() {
    const touchMessages = pioConfig.dialog?.touch;
    if (touchMessages) {
        const arr = Array.isArray(touchMessages) ? touchMessages : [touchMessages];
        displayDialog(randomPick(arr));
    }
    resetIdleTimer();
}

// === Live2D 初始化 ===
async function initLive2D() {
    if (typeof window === "undefined") return;

    try {
        const PIXI = await import("pixi.js");
        window.PIXI = PIXI;

        const Live2DModule = await import("pixi-live2d-display/cubism4");
        const { Live2DModel } = Live2DModule;

        Live2DModel.prototype.registerInteraction = function() {};
        Live2DModel.prototype.unregisterInteraction = function() {};

        const width = pioConfig.width || 280;
        const height = pioConfig.height || 350;

        app = new PIXI.Application({
            view: canvas,
            width: width,
            height: height,
            backgroundAlpha: 0,
            resolution: window.devicePixelRatio || 1,
            autoDensity: true,
        });

        model = await Live2DModel.from(modelPath);

        const scale = 0.15;
        model.scale.set(scale);
        model.anchor.set(0.5, 0.5);
        model.x = width / 2;
        model.y = height / 2 + 50;

        app.stage.addChild(model);

        canvas.addEventListener("mousemove", (e) => {
            if (!model || !model.internalModel) return;
            const rect = canvas.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
            model.internalModel.focusController?.focus(x, -y);
        });

        canvas.addEventListener("click", () => {
            if (!model || !model.internalModel) return;
            const expressions = model.internalModel.motionManager?.expressionManager?.definitions;
            if (expressions && expressions.length > 0) {
                const randomIndex = Math.floor(Math.random() * expressions.length);
                model.expression(randomIndex);
            }
        });

        console.log("Live2D 白猫娘模型加载成功！");

        // 加载完成后显示欢迎 / 时间问候
        const timeGreeting = getTimeGreeting();
        const welcomeMsg = pioConfig.dialog?.welcome;
        if (timeGreeting) {
            displayDialog(timeGreeting);
        } else if (welcomeMsg) {
            const text = Array.isArray(welcomeMsg) ? randomPick(welcomeMsg) : welcomeMsg;
            displayDialog(text);
        }

        resetIdleTimer();
    } catch (error) {
        console.error("Live2D 模型加载失败:", error);
    }
}

// === 拖拽 ===
function handleMouseDown(e) {
    if (pioConfig.mode === "draggable") {
        isDragging = true;
        dragStartX = e.clientX - positionX;
        dragStartY = e.clientY - positionY;
    }
    resetIdleTimer();
}

function handleMouseMove(e) {
    if (isDragging) {
        positionX = e.clientX - dragStartX;
        positionY = e.clientY - dragStartY;
    }
}

function handleMouseUp() {
    isDragging = false;
}

function handleUserActivity() {
    resetIdleTimer();
}

// === 生命周期 ===
onMount(() => {
    if (!pioConfig.enable) return;

    // 移动端检测：768px 以下完全不初始化
    if (window.matchMedia("(max-width: 768px)").matches) {
        isMobile = true;
        return;
    }

    initLive2D();

    if (pioConfig.mode === "draggable") {
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseup", handleMouseUp);
    }

    window.addEventListener("scroll", handleUserActivity);
    window.addEventListener("keydown", handleUserActivity);
});

onDestroy(() => {
    if (typeof window === "undefined") return;

    if (app) {
        app.destroy(true, { children: true, texture: true, baseTexture: true });
        app = null;
    }
    if (dialogTimer) clearTimeout(dialogTimer);
    if (idleTimer) clearTimeout(idleTimer);
    window.removeEventListener("mousemove", handleMouseMove);
    window.removeEventListener("mouseup", handleMouseUp);
    window.removeEventListener("scroll", handleUserActivity);
    window.removeEventListener("keydown", handleUserActivity);
});
</script>

{#if pioConfig.enable && !isMobile}
    <!-- 看板娘主体：用 CSS class 控制显隐，不销毁 DOM -->
    <div
        class="live2d-container {pioConfig.position || 'right'}"
        class:widget-hidden={!isWidgetVisible}
        style="transform: translate({positionX}px, {positionY}px);"
        on:mousedown={handleMouseDown}
        on:click={handleContainerClick}
    >
        <!-- 关闭按钮：在容器内部，跟随拖拽 -->
        <button
            class="live2d-close"
            on:click|stopPropagation={toggleWidget}
            title="收起看板娘"
        >✕</button>

        <!-- 对话气泡 -->
        {#if showDialog && currentDialog}
            <div class="dialog-bubble">
                <span>{currentDialog}</span>
            </div>
        {/if}

        <canvas bind:this={canvas}></canvas>
    </div>

    <!-- 展开按钮：仅在收起状态显示，位置避开底部音乐栏 -->
    {#if !isWidgetVisible}
        <button
            class="live2d-expand {pioConfig.position || 'right'}"
            on:click={toggleWidget}
            title="展开看板娘"
        >
            <span class="expand-icon">💬</span>
            <span class="expand-label">看板娘</span>
        </button>
    {/if}
{/if}

<style>
/* === 看板娘容器 === */
.live2d-container {
    position: fixed;
    bottom: 0;
    z-index: 9999;
    cursor: grab;
    pointer-events: auto;
    transition: opacity 0.4s ease, transform 0.4s ease;
}

.live2d-container.widget-hidden {
    opacity: 0;
    pointer-events: none;
    transform: translateY(100%) !important;
}

.live2d-container:active {
    cursor: grabbing;
}

.live2d-container.left {
    left: 0;
}

.live2d-container.right {
    right: 0;
}

.live2d-container canvas {
    display: block;
}

/* === 容器内关闭按钮 === */
.live2d-close {
    position: absolute;
    top: 4px;
    right: 4px;
    z-index: 10002;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: none;
    background: rgba(0, 0, 0, 0.15);
    color: rgba(255, 255, 255, 0.8);
    font-size: 11px;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.2s ease, background 0.2s ease;
    pointer-events: auto;
}

.live2d-container:hover .live2d-close {
    opacity: 0.6;
}

.live2d-close:hover {
    opacity: 1 !important;
    background: rgba(0, 0, 0, 0.35);
}

/* === 对话气泡 === */
.dialog-bubble {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 8px 14px;
    max-width: 200px;
    min-width: 60px;
    font-size: 13px;
    line-height: 1.5;
    color: #444;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    pointer-events: none;
    animation: bubble-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 10001;
    white-space: pre-wrap;
    word-break: break-word;
    backdrop-filter: blur(12px);
}

.dialog-bubble::after {
    content: "";
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid rgba(255, 255, 255, 0.92);
}

/* === 展开按钮（仅收起后显示，避开底部音乐栏） === */
.live2d-expand {
    position: fixed;
    bottom: 100px;
    z-index: 10000;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 14px;
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.85);
    color: #555;
    font-size: 13px;
    cursor: pointer;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.25s ease;
    backdrop-filter: blur(8px);
    animation: fade-in 0.3s ease;
}

.live2d-expand:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.live2d-expand.left {
    left: 12px;
}

.live2d-expand.right {
    right: 12px;
}

.expand-icon {
    font-size: 16px;
    line-height: 1;
}

.expand-label {
    font-size: 13px;
    line-height: 1;
}

/* === 动画 === */
@keyframes bubble-in {
    0% {
        opacity: 0;
        transform: translateX(-50%) scale(0.6);
    }
    100% {
        opacity: 1;
        transform: translateX(-50%) scale(1);
    }
}

@keyframes fade-in {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* 手机端隐藏 */
@media (max-width: 768px) {
    .live2d-container,
    .live2d-expand {
        display: none !important;
    }
}
</style>
