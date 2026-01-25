<script lang="ts">
    import { onMount } from 'svelte';
    import Icon from '@iconify/svelte';
    import { fade, fly } from 'svelte/transition';

    // API 地址：开发环境用 localhost，生产用相对路径
    const API_BASE = import.meta.env.DEV 
        ? `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000` 
        : '';

    // 默认配置
    export let githubUser = 'AVIDS2';
    export let bilibiliFavId = '3845617847'; // 收藏夹 ID

    let activeTab = 'github'; // github, bilibili, tools
    let githubStars = [];
    let bilibiliFavs = [];
    let tools = {}; // 按分类分组的工具
    let loading = true;

    async function fetchGitHubStars() {
        try {
            const res = await fetch(`https://api.github.com/users/${githubUser}/starred?per_page=30`);
            if (res.ok) githubStars = await res.json();
        } catch (e) {
            console.error('GitHub fetch failed', e);
        }
    }

    async function fetchBilibiliFavs() {
        try {
            // 通过后端代理获取 B 站数据
            const res = await fetch(`${API_BASE}/api/bilibili/favorites/${bilibiliFavId}?page_size=20`);
            if (res.ok) {
                const data = await res.json();
                bilibiliFavs = data.items || [];
            }
        } catch (e) {
            console.error('Bilibili fetch failed', e);
        }
    }

    async function fetchTools() {
        try {
            const res = await fetch(`${API_BASE}/api/tools`);
            if (res.ok) {
                tools = await res.json();
            }
        } catch (e) {
            console.error('Tools fetch failed', e);
        }
    }

    function fixUrl(url) {
        if (!url) return '';
        if (url.startsWith('http')) return url;
        
        // 如果是相对路径，且在开发环境下，拼接 API_BASE
        const normalizedPath = url.startsWith('/') ? url : `/${url}`;
        return import.meta.env.DEV ? `${API_BASE}${normalizedPath}` : normalizedPath;
    }

    onMount(async () => {
        loading = true;
        await Promise.all([fetchGitHubStars(), fetchBilibiliFavs(), fetchTools()]);
        loading = false;
    });
</script>

<div class="collections-container">
    <!-- Tabs (签子) -->
    <div class="flex flex-wrap gap-2 mb-8 bg-[var(--btn-regular-bg)] p-1.5 rounded-xl w-fit">
        <button 
            class="px-6 py-2 rounded-lg transition-all flex items-center gap-2 {activeTab === 'github' ? 'bg-[var(--primary)] text-white shadow-md font-bold' : 'text-black dark:text-white hover:bg-white/50 dark:hover:bg-white/10'}"
            on:click={() => activeTab = 'github'}
        >
            <Icon icon="fa6-brands:github" /> GitHub Stars
        </button>
        <button 
            class="px-6 py-2 rounded-lg transition-all flex items-center gap-2 {activeTab === 'bilibili' ? 'bg-[#fb7299] text-white shadow-md font-bold' : 'text-black dark:text-white hover:bg-white/50 dark:hover:bg-white/10'}"
            on:click={() => activeTab = 'bilibili'}
        >
            <Icon icon="ri:bilibili-fill" /> Bilibili 收藏
        </button>
        <button 
            class="px-6 py-2 rounded-lg transition-all flex items-center gap-2 {activeTab === 'tools' ? 'bg-[#4dabf7] text-white shadow-md font-bold' : 'text-black dark:text-white hover:bg-white/50 dark:hover:bg-white/10'}"
            on:click={() => activeTab = 'tools'}
        >
            <Icon icon="material-symbols:hand-repair" /> 实用工具
        </button>
    </div>

    <!-- Content Area -->
    <div class="relative min-h-[400px]">
        {#if loading}
            <div class="flex items-center justify-center py-20" in:fade>
                <div class="animate-spin rounded-full h-12 w-12 border-4 border-[var(--primary)] border-t-transparent"></div>
            </div>
        {:else}
            {#if activeTab === 'github'}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4" in:fly={{ y: 20, duration: 400 }}>
                    {#each githubStars as repo}
                        <a href={repo.html_url} target="_blank" class="card-base p-4 hover:border-[var(--primary)] transition-all group">
                            <div class="flex justify-between items-start mb-2">
                                <h3 class="font-bold text-lg group-hover:text-[var(--primary)]">{repo.name}</h3>
                                <div class="flex items-center gap-1 text-sm text-50">
                                    <Icon icon="material-symbols:star" class="text-yellow-500" />
                                    {repo.stargazers_count}
                                </div>
                            </div>
                            <p class="text-sm text-60 line-clamp-2 mb-3">{repo.description || 'No description'}</p>
                            <div class="flex items-center gap-3 text-xs text-40">
                                <span class="flex items-center gap-1">
                                    <div class="w-3 h-3 rounded-full" style="background: {repo.language === 'TypeScript' ? '#3178c6' : '#f1e05a'}"></div>
                                    {repo.language}
                                </span>
                            </div>
                        </a>
                    {/each}
                </div>
            {:else if activeTab === 'bilibili'}
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" in:fly={{ y: 20, duration: 400 }}>
                    {#each bilibiliFavs as video}
                        <a href={video.link} target="_blank" class="card-base overflow-hidden group">
                            <div class="aspect-video bg-gray-200 dark:bg-gray-800 relative overflow-hidden">
                                <img src={fixUrl(video.cover)} alt={video.title} referrerPolicy="no-referrer" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                                <div class="absolute inset-0 bg-black/20 group-hover:bg-black/0 transition-colors"></div>
                                <div class="absolute bottom-2 right-2 bg-black/60 text-white text-[10px] px-2 py-0.5 rounded">Bilibili</div>
                            </div>
                            <div class="p-3">
                                <h3 class="font-medium text-sm line-clamp-2 group-hover:text-[#fb7299]">{video.title}</h3>
                            </div>
                        </a>
                    {/each}
                </div>
            {:else if activeTab === 'tools'}
                <div class="space-y-8" in:fly={{ y: 20, duration: 400 }}>
                    {#if Object.keys(tools).length === 0}
                        <div class="card-base p-12 text-center text-gray-500">
                            <Icon icon="material-symbols:inventory-2-outline" class="text-5xl mb-4 opacity-50" />
                            <p>暂无收藏的工具</p>
                            <p class="text-sm mt-2">去管理后台添加吧！</p>
                        </div>
                    {:else}
                        {#each Object.entries(tools) as [category, items]}
                            <div class="card-base p-6">
                                <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                                    <Icon icon="material-symbols:folder-open" class="text-[var(--primary)]" />
                                    {category}
                                </h3>
                                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {#each items as tool}
                                        <a href={tool.url} target="_blank" class="flex items-start gap-3 p-3 rounded-xl hover:bg-[var(--btn-regular-bg)] transition-colors group">
                                            {#if tool.icon}
                                                <img src={fixUrl(tool.icon)} alt={tool.name} class="w-10 h-10 rounded-lg object-cover" />
                                            {:else}
                                                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--primary)] to-purple-500 flex items-center justify-center text-white font-bold">
                                                    {tool.name.charAt(0)}
                                                </div>
                                            {/if}
                                            <div class="flex-1 min-w-0">
                                                <h4 class="font-medium group-hover:text-[var(--primary)] transition-colors">{tool.name}</h4>
                                                <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">{tool.description || '暂无描述'}</p>
                                            </div>
                                            <Icon icon="material-symbols:arrow-outward" class="text-gray-400 group-hover:text-[var(--primary)] transition-colors" />
                                        </a>
                                    {/each}
                                </div>
                            </div>
                        {/each}
                    {/if}
                </div>
            {/if}
        {/if}
    </div>
</div>

<style>
    .card-base {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 1rem;
    }
    
    /* 暗色模式适配 */
    :global(.dark) .card-base {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    /* 暗色模式下所有文字变白 */
    :global(.dark) .card-base h3,
    :global(.dark) .card-base h4 {
        color: #ffffff !important;
    }
    
    :global(.dark) .card-base p,
    :global(.dark) .card-base span,
    :global(.dark) .card-base div {
        color: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* Tab 按钮暗色模式 */
    :global(.dark) .collections-container > div:first-child {
        background: rgba(30, 41, 59, 0.6);
    }
    
    /* Tab 按钮文字暗色模式 */
    :global(.dark) .collections-container > div:first-child button {
        color: rgba(255, 255, 255, 0.9) !important;
    }
</style>
