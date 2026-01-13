---
title: 实用命令行工具整理
published: 2026-01-11
description: 替代传统命令的现代工具：eza、zoxide、fzf、bat、ripgrep等
tags: [命令行, 工具推荐, 效率, 开发者]
category: 工具
image: https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=1200
draft: false
---

整理一些可以替代传统Unix命令的现代工具，主要改进是更好的默认输出和更快的速度。

## 文件管理

### eza（替代ls）

```bash
# 安装
brew install eza  # macOS
cargo install eza # 通用

# 使用
eza -la --icons --git
```

![终端界面](https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=800)

输出改进：
- 文件类型图标
- Git状态显示
- 人类可读的文件大小

### zoxide（替代cd）

记住访问过的目录，支持模糊跳转：

```bash
brew install zoxide
eval "$(zoxide init zsh)"  # 添加到.zshrc

# 使用
z projects  # 跳转到最常访问的projects目录
z blog      # 模糊匹配
```

### fzf（模糊搜索）

```bash
brew install fzf

# 搜索文件
fzf

# 组合使用
vim $(fzf)
cd $(find . -type d | fzf)
```

## 文件查看

### bat（替代cat）

语法高亮，自动分页：

```bash
brew install bat
bat app.py
```

### delta（git diff增强）

```bash
brew install git-delta

# ~/.gitconfig
[core]
    pager = delta
[delta]
    side-by-side = true
```

改进效果：左右对比视图，语法高亮。

## 搜索工具

### ripgrep（替代grep）

速度比grep快很多：

```bash
brew install ripgrep

rg "function"
rg "TODO" -t python
rg "bug" -g "!node_modules"
```

### fd（替代find）

```bash
brew install fd

fd "\.py$"
fd "\.log$" -x rm {}
```

![代码搜索](https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800)

## 系统监控

### btop（替代top）

```bash
brew install btop
btop
```

显示CPU、内存、网络、磁盘IO，支持进程搜索和终止。

### dust（磁盘占用分析）

```bash
brew install dust
dust
```

可视化显示各目录占用空间。

## Git增强

### lazygit

终端Git GUI：

```bash
brew install lazygit
lazygit
```

键盘操作完成暂存、提交、分支管理、rebase等操作。

### gh

GitHub官方CLI：

```bash
brew install gh
gh auth login

gh pr create
gh issue list
gh repo clone owner/repo
```

## 终端配置

### Oh My Zsh + Powerlevel10k

```bash
# Oh My Zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Powerlevel10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

# ~/.zshrc
ZSH_THEME="powerlevel10k/powerlevel10k"
```

## 配置示例

```bash
# ~/.zshrc 别名配置
alias ls="eza -la --icons --git"
alias cat="bat"
alias find="fd"
alias grep="rg"
alias top="btop"
alias lg="lazygit"

eval "$(zoxide init zsh)"
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
```

## 批量安装

macOS：
```bash
brew install eza zoxide fzf bat git-delta ripgrep fd btop lazygit gh
```

Linux（使用cargo安装的工具）：
```bash
cargo install eza zoxide bat fd-find ripgrep
```

![开发环境](https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800)

---

*这些工具大多是Rust编写的，性能都不错。*
