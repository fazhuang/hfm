<script setup lang="ts">
/**
 * AppFooter — institutional footer (UI-02).
 * Co-construction signature uses FULL official names (CR-001/006):
 * 甘肃医学院 × 灵台县皇甫谧中医针灸传承创新示范中心.
 * Platform positioning: 官方公益性文化传播平台（非商业用途）.
 */
import { RouterLink } from 'vue-router'

defineOptions({ name: 'AppFooter' })
</script>

<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <div class="app-footer__signature">
        <p class="app-footer__platform">皇甫谧人文数字平台</p>
        <p class="app-footer__institutions">
          甘肃医学院 × 灵台县皇甫谧中医针灸传承创新示范中心 · 共建
        </p>
        <p class="app-footer__statement">
          官方公益性文化传播平台（非商业、无盈利目的）· 客户提供资料已获授权公开
        </p>
      </div>
      <nav class="app-footer__nav" aria-label="页脚导航">
        <RouterLink to="/about">关于平台</RouterLink>
        <RouterLink to="/about#compliance">版权与免责声明</RouterLink>
        <RouterLink to="/about#privacy">隐私说明</RouterLink>
      </nav>
    </div>
    <p class="app-footer__copy">仅供皇甫谧学术研究、教学与文化传播使用；不提供任何临床诊疗建议。</p>
  </footer>
</template>

<style scoped>
.app-footer {
  border-top: 1px solid var(--hfm-color-border);
  background: var(--hfm-color-surface);
  color: var(--hfm-color-text-muted);
  font-size: var(--hfm-text-sm);
  padding: var(--hfm-space-6) var(--hfm-space-6) var(--hfm-space-4);
}

.app-footer__inner {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: var(--hfm-space-4);
  justify-content: space-between;
}

.app-footer__signature p {
  margin: 0 0 var(--hfm-space-1);
}

.app-footer__platform {
  font-family: var(--hfm-font-serif);
  font-size: var(--hfm-text-lg);
  color: var(--hfm-color-text);
}

.app-footer__institutions {
  color: var(--hfm-color-text-secondary);
}

.app-footer__nav {
  display: flex;
  gap: var(--hfm-space-4);
  flex-wrap: wrap;
  align-items: flex-start;
}

.app-footer__nav a {
  color: var(--hfm-color-interactive);
  text-decoration: none;
}

.app-footer__nav a:hover {
  color: var(--hfm-color-accent-hover);
  text-decoration: underline;
}

.app-footer__copy {
  max-width: var(--hfm-content-max);
  margin: var(--hfm-space-4) auto 0;
  border-top: 1px solid var(--hfm-color-border);
  padding-top: var(--hfm-space-3);
  font-size: var(--hfm-text-xs);
}
</style>
