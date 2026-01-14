import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.dwill.admin',
  appName: 'DWill Admin',
  webDir: '../static/admin',
  server: {
    // APK 运行时连接的服务器地址
    // 改成你的实际域名
    url: 'https://blog.dwill.top:7777/admin',
    cleartext: true
  }
};

export default config;
