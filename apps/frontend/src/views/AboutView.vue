<script setup lang="ts">
/**
 * AboutView — 关于平台（UI-02；页脚入口）。
 * 平台定位 / 政校共建 / 内容与版权 / 隐私说明 / 免责声明（含非临床诊疗边界）。
 */
defineOptions({ name: 'AboutView' })
</script>

<template>
  <section class="about" aria-labelledby="about-heading">
    <h1 id="about-heading">关于平台</h1>

    <h2>平台定位</h2>
    <p>
      皇甫谧人文数字平台是以皇甫谧为核心文化
      IP，以权威数字人文资料为基础，以医学本科院校科研教学能力为支撑，
      以地方政府非遗文化传播为公共出口的官方公益性文化传播平台（非商业、无盈利目的）。
    </p>

    <h2>政校共建</h2>
    <p>平台由甘肃医学院与灵台县皇甫谧中医针灸传承创新示范中心共建（正式机构署名，CR-001/006）。</p>

    <h2 id="content">内容与版权</h2>
    <p>
      平台所展示的客户提供资料统一视为已获授权并允许公开发布；后续如产生版权问题由客户后置解决。
      平台以非商业、非盈利方式用于皇甫谧学术研究、教学与文化传播。
    </p>

    <h2 id="privacy">隐私说明</h2>
    <p>
      平台公开展示遵循隐私分级：职业与学术公共身份信息正常展示；证书编号、签字、联系方式等个人敏感信息经脱敏后展示；
      法人证照原件、考评员名单等不应公共展示的信息不进入公开投影。任何个人信息问题请通过建设方联系处理。
    </p>

    <h2 id="compliance">版权与免责声明</h2>
    <p>
      本平台为学术资料展示平台，内容仅供学习、研究与文化传播；请勿用于商业用途。
      平台明确不提供任何临床诊断、治疗建议或穴位处方推荐（历史医学内容仅作学术资料展示）。
    </p>
  </section>
</template>

<style scoped>
.about {
  max-width: var(--hfm-content-max);
  margin: 0 auto;
}

.about h2 {
  margin-top: var(--hfm-space-12);
}

.about p {
  max-width: 68ch;
  line-height: var(--hfm-leading-reading);
}
</style>
