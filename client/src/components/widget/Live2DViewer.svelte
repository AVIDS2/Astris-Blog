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

// 模型路径 - 使用白猫娘模型
const modelPath = pioConfig.models?.[0] || "/pio/models/whitecat/sdwhite cat free.model3.json";

async function initLive2D() {
    if (typeof window === "undefined") return;

    try {
        // 动态导入 PIXI 和 live2d-display (专门使用 Cubism 4 版本)
        const PIXI = await import("pixi.js");
        
        // 将 PIXI 暴露给 live2d-display (必须在导入 live2d-display 之前)
        window.PIXI = PIXI;
        
        // 使用 Cubism 4 专用版本，避免依赖 Cubism 2 runtime
        const Live2DModule = await import("pixi-live2d-display/cubism4");
        const { Live2DModel } = Live2DModule;

        // 禁用自动交互注册以避免 PIXI v7 兼容性问题
        // pixi-live2d-display 的 registerInteraction 使用了已废弃的 PIXI v6 API
        // 必须在原型链上覆盖，因为这是实例方法，在 _render 时被调用
        Live2DModel.prototype.registerInteraction = function() {};
        Live2DModel.prototype.unregisterInteraction = function() {};

        const width = pioConfig.width || 280;
        const height = pioConfig.height || 350;

        // 创建 PIXI 应用 (PIXI v7 API - 选项直接传递给构造函数)
        app = new PIXI.Application({
            view: canvas,
            width: width,
            height: height,
            backgroundAlpha: 0,
            resolution: window.devicePixelRatio || 1,
            autoDensity: true,
        });

        // 加载 Live2D 模型
        model = await Live2DModel.from(modelPath);

        // 设置模型大小和位置
        const scale = 0.15; // 根据模型大小调整
        model.scale.set(scale);
        model.anchor.set(0.5, 0.5);
        model.x = width / 2;
        model.y = height / 2 + 50;

        app.stage.addChild(model);

        // 手动实现鼠标跟踪 - 直接监听 canvas 事件 (替代已废弃的 PIXI 交互管理器)
        canvas.addEventListener("mousemove", (e) => {
            if (!model || !model.internalModel) return;
            const rect = canvas.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
            model.internalModel.focusController?.focus(x, -y);
        });

        // 手动实现点击交互
        canvas.addEventListener("click", () => {
            if (!model || !model.internalModel) return;
            // 尝试播放随机表情
            const expressions = model.internalModel.motionManager?.expressionManager?.definitions;
            if (expressions && expressions.length > 0) {
                const randomIndex = Math.floor(Math.random() * expressions.length);
                model.expression(randomIndex);
            }
        });

        console.log("Live2D (Cubism 3/4) 白猫娘模型加载成功！模型已渲染到画布。");
    } catch (error) {
        console.error("Live2D 模型加载失败:", error);
    }
}

function handleMouseDown(e) {
    if (pioConfig.mode === "draggable") {
        isDragging = true;
        dragStartX = e.clientX - positionX;
        dragStartY = e.clientY - positionY;
    }
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

onMount(() => {
    if (!pioConfig.enable) return;

    // 手机端隐藏检查
    if (pioConfig.hiddenOnMobile && window.matchMedia("(max-width: 1280px)").matches) {
        return;
    }

    initLive2D();

    // 添加全局拖拽监听
    if (pioConfig.mode === "draggable") {
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseup", handleMouseUp);
    }
});

onDestroy(() => {
    if (typeof window === "undefined") return;
    
    if (app) {
        app.destroy(true, { children: true, texture: true, baseTexture: true });
        app = null;
    }
    window.removeEventListener("mousemove", handleMouseMove);
    window.removeEventListener("mouseup", handleMouseUp);
});
</script>

{#if pioConfig.enable}
    <div 
        class="live2d-container {pioConfig.position || 'right'}"
        style="transform: translate({positionX}px, {positionY}px);"
        on:mousedown={handleMouseDown}
    >
        <canvas bind:this={canvas}></canvas>
    </div>
{/if}

<style>
.live2d-container {
    position: fixed;
    bottom: 0;
    z-index: 9999;
    cursor: grab;
    pointer-events: auto;
}

/* 手机端彻底隐藏 */
@media (max-width: 768px) {
    .live2d-container {
        display: none !important;
    }
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
</style>
