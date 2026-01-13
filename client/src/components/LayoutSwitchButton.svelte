<script lang="ts">
import { onMount } from "svelte";
import { sidebarLayoutConfig, siteConfig } from "../config";

// 当前侧边栏模式：both = 双侧边栏，unilateral = 单侧边栏
let currentMode: "both" | "unilateral" = "both";

let mounted = false;
let isSmallScreen = false;
let isSwitching = false;

// 配置中的默认模式
const configMode = sidebarLayoutConfig.position;

function checkScreenSize() {
	isSmallScreen = window.innerWidth < 1200;
}

// 同步布局状态
function syncLayoutFromDOM() {
	const rightSidebar = document.querySelector(".right-sidebar-container");
	if (rightSidebar) {
		const isHidden = rightSidebar.classList.contains("hidden-by-user") || 
		                 rightSidebar.style.display === "none";
		currentMode = isHidden ? "unilateral" : "both";
	}
}

onMount(() => {
	mounted = true;
	checkScreenSize();

	// 从 localStorage 读取用户偏好
	const savedMode = localStorage.getItem("sidebarMode");
	if (savedMode && (savedMode === "both" || savedMode === "unilateral")) {
		currentMode = savedMode;
		// 应用保存的模式（无动画）
		setTimeout(() => applySidebarMode(currentMode, false), 50);
	} else {
		// 使用配置中的默认模式
		currentMode = configMode === "both" ? "both" : "unilateral";
	}

	// 延迟同步 DOM 状态
	setTimeout(syncLayoutFromDOM, 100);

	// 监听窗口大小变化
	window.addEventListener("resize", checkScreenSize);

	return () => {
		window.removeEventListener("resize", checkScreenSize);
	};
});

function applySidebarMode(mode: "both" | "unilateral", animate: boolean = true) {
	const rightSidebar = document.querySelector(".right-sidebar-container") as HTMLElement;
	const mainGrid = document.getElementById("main-grid");
	
	if (!mainGrid) return;

	// 统一的动画参数，与 MainGridLayout.astro 保持一致
	const transitionDuration = 450;
	
	if (mode === "unilateral") {
		const transitionDuration = animate ? 450 : 0;
		if (animate) {
			mainGrid.setAttribute("data-sidebar-mode", "unilateral");
			if (rightSidebar) {
				// 隐藏时，透明度消失要比宽度变化快一点，避免看到挤压的内容
				rightSidebar.style.transition = `opacity 0.2s ease-out, transform ${transitionDuration}ms cubic-bezier(0.68, -0.15, 0.265, 1.15)`;
				rightSidebar.style.opacity = "0";
				rightSidebar.style.transform = "translateX(40px)";
				rightSidebar.style.pointerEvents = "none";
				
				setTimeout(() => {
					rightSidebar.style.display = "none";
				}, transitionDuration);
			}
		} else {
			mainGrid.setAttribute("data-sidebar-mode", "unilateral");
			if (rightSidebar) {
				rightSidebar.style.display = "none";
				rightSidebar.style.opacity = "0";
			}
		}
	} else {
		const transitionDuration = animate ? 450 : 0;
		if (rightSidebar) {
			rightSidebar.style.display = "";
			// 强制重排
			rightSidebar.offsetHeight;
			
			if (animate) {
				mainGrid.setAttribute("data-sidebar-mode", "both");
				// 显示时，透明度可以稍微滞后一点点
				rightSidebar.style.transition = `opacity 0.4s ease-out 0.1s, transform ${transitionDuration}ms cubic-bezier(0.68, -0.15, 0.265, 1.15)`;
				requestAnimationFrame(() => {
					rightSidebar.style.opacity = "1";
					rightSidebar.style.transform = "translateX(0)";
					rightSidebar.style.pointerEvents = "auto";
				});
			} else {
				mainGrid.setAttribute("data-sidebar-mode", "both");
				rightSidebar.style.opacity = "1";
				rightSidebar.style.transform = "translateX(0)";
				rightSidebar.style.pointerEvents = "auto";
			}
		}
	}
}

function switchSidebarMode() {
	if (!mounted || isSmallScreen || isSwitching) return;

	isSwitching = true;
	currentMode = currentMode === "both" ? "unilateral" : "both";
	localStorage.setItem("sidebarMode", currentMode);

	// 应用模式变化
	applySidebarMode(currentMode);

	// 触发自定义事件
	const event = new CustomEvent("sidebarModeChange", {
		detail: { mode: currentMode },
	});
	window.dispatchEvent(event);

	// 动画完成后重置状态
	setTimeout(() => {
		isSwitching = false;
	}, 500);
}

// 监听侧边栏模式变化事件
onMount(() => {
	const handleModeChange = (
		event: CustomEvent<{ mode: "both" | "unilateral" }>,
	) => {
		currentMode = event.detail.mode;
	};

	window.addEventListener("sidebarModeChange", handleModeChange as EventListener);

	return () => {
		window.removeEventListener("sidebarModeChange", handleModeChange as EventListener);
	};
});

// 监听 Swup 页面切换
onMount(() => {
	const handleSwupEvent = () => {
		setTimeout(() => {
			const savedMode = localStorage.getItem("sidebarMode");
			if (savedMode && (savedMode === "both" || savedMode === "unilateral")) {
				currentMode = savedMode;
				applySidebarMode(currentMode);
			}
			syncLayoutFromDOM();
		}, 200);
	};

	function setupSwupListeners() {
		if (typeof window !== "undefined" && (window as any).swup) {
			const swup = (window as any).swup;
			swup.hooks.on("content:replace", handleSwupEvent);
			swup.hooks.on("page:view", handleSwupEvent);
			swup.hooks.on("animation:in:end", handleSwupEvent);
		} else {
			window.addEventListener("popstate", handleSwupEvent);
		}
	}

	setTimeout(setupSwupListeners, 100);

	return () => {
		if (typeof window !== "undefined" && (window as any).swup) {
			const swup = (window as any).swup;
			swup.hooks.off("content:replace", handleSwupEvent);
			swup.hooks.off("page:view", handleSwupEvent);
			swup.hooks.off("animation:in:end", handleSwupEvent);
		} else {
			window.removeEventListener("popstate", handleSwupEvent);
		}
	};
});
</script>

{#if mounted && !isSmallScreen && configMode === "both"}
  <button 
    aria-label="切换侧边栏布局" 
    class="btn-plain scale-animation rounded-lg h-11 w-11 active:scale-90 flex items-center justify-center theme-switch-btn {isSwitching ? 'switching' : ''}" 
    on:click={switchSidebarMode}
    disabled={isSwitching}
    title={currentMode === 'both' ? '隐藏右侧边栏' : '显示右侧边栏'}
  >
      {#if currentMode === 'both'}
        <!-- 双侧边栏图标 -->
        <svg class="w-5 h-5 icon-transition" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 3h18v18H3V3zm2 2v14h4V5H5zm6 0v14h8V5h-8z"/>
        </svg>
    {:else}
      <!-- 单侧边栏图标 -->
      <svg class="w-5 h-5 icon-transition" fill="currentColor" viewBox="0 0 24 24">
        <path d="M3 3h18v18H3V3zm2 2v14h4V5H5zm6 0v14h8V5h-8z" opacity="0.5"/>
        <path d="M3 3h8v18H3V3zm2 2v14h4V5H5z"/>
      </svg>
    {/if}
  </button>
{/if}

<style>
    /* 确保主题切换按钮的背景色即时更新 */
    .theme-switch-btn::before {
        transition: transform 75ms ease-out, background-color 0ms !important;
    }

    /* 图标过渡动画 */
    .icon-transition {
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
    }

    /* 切换中的按钮动画 */
    .switching {
        pointer-events: none;
    }

    .switching .icon-transition {
        animation: iconRotate 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes iconRotate {
        0% {
            transform: rotate(0deg) scale(1);
            opacity: 1;
        }
        50% {
            transform: rotate(180deg) scale(0.8);
            opacity: 0.5;
        }
        100% {
            transform: rotate(360deg) scale(1);
            opacity: 1;
        }
    }

    /* 悬停效果增强 */
    .theme-switch-btn:not(.switching):hover .icon-transition {
        transform: scale(1.1);
    }

    /* 按钮禁用状态 */
    .theme-switch-btn:disabled {
        cursor: not-allowed;
        opacity: 0.7;
    }
</style>
