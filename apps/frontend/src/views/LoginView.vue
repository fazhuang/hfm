<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref<string | null>(null)
const busy = ref(false)

async function onSubmit(): Promise<void> {
  error.value = null
  busy.value = true
  try {
    await store.login(username.value, password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/research'
    await router.push(redirect)
  } catch {
    error.value = '登录失败：请检查凭据或会话已失效。'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="login" aria-labelledby="login-heading">
    <h1 id="login-heading">登录</h1>
    <form class="login__form" @submit.prevent="onSubmit">
      <label for="login-username">用户名</label>
      <input id="login-username" v-model="username" type="text" autocomplete="username" />
      <label for="login-password">密码</label>
      <input
        id="login-password"
        v-model="password"
        type="password"
        autocomplete="current-password"
      />
      <p v-if="error" class="login__error" role="alert">{{ error }}</p>
      <button type="submit" :disabled="busy">登录</button>
    </form>
  </section>
</template>

<style scoped>
.login__form {
  display: grid;
  gap: var(--hfm-space-2);
  max-width: 24rem;
}

.login__error {
  color: var(--hfm-color-danger);
}
</style>
