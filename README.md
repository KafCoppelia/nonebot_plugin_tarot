<div align="center">

# Tarot

_🔮 塔罗牌 🔮_

</div>

<p align="center">

  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot2-2.0.0+-green">
  </a>

  <a href="https://github.com/MinatoAquaCrews/nonebot_plugin_tarot/releases/tag/v0.5.0a6">
    <img src="https://img.shields.io/github/v/release/MinatoAquaCrews/nonebot_plugin_tarot?color=orange">
  </a>

  <a href="https://www.codefactor.io/repository/github/MinatoAquaCrews/nonebot_plugin_tarot">
    <img src="https://img.shields.io/codefactor/grade/github/MinatoAquaCrews/nonebot_plugin_tarot/master?color=red">
  </a>

  <a href="https://github.com/MinatoAquaCrews/nonebot_plugin_tarot">
    <img src="https://img.shields.io/pypi/dm/nonebot_plugin_tarot">
  </a>

  <a href="https://results.pre-commit.ci/latest/github/MinatoAquaCrews/nonebot_plugin_tarot/master">
	  <img src="https://results.pre-commit.ci/badge/github/MinatoAquaCrews/nonebot_plugin_tarot/master.svg" alt="pre-commit.ci status">
  </a>

## 序

_“许多傻瓜对千奇百怪的迷信说法深信不疑：象牙、护身符、黑猫、打翻的盐罐、驱邪、占卜、符咒、毒眼、塔罗牌、星象、水晶球、咖啡渣、手相、预兆、预言还有星座。”——《人类愚蠢辞典》_

## 版本

🧰 [v0.5.0a6](https://github.com/MinatoAquaCrews/nonebot_plugin_tarot/releases/tag/v0.5.0a6)

⚠ 适配nonebot2-2.0.0+

## 安装

1. 安装方式
   - 通过 `pip` 或 `nb-cli` 安装。pypi无法发行过大安装包，由此安装的插件不包含 `./resource` 下提供的塔罗牌主题资源。仓库提供了两种塔罗牌主题，可在 [v0.4.0 release](https://github.com/MinatoAquaCrews/nonebot_plugin_tarot/releases/tag/v0.4.0) Assets下载，部署至本地后修改 `TAROT_PATH` 配置即可；

   - 通过 `zip` 或 `git clone` 安装：包含 `resource` 下所有塔罗牌主题资源；

2. `CHAIN_REPLY` 设置全局群聊转发模式（避免刷屏），可通过命令开启或关闭，默认开启；

3. `env` 下设置 `TAROT_PATH` 以更改资源路径，该目录下存放各塔罗牌主题图片（子目录表示不同主题）。默认为 `nonebot_plugin_localstore` 为本插件提供的路径。例如：

   ```toml
   TAROT_PATH="path-to-MyTarotResource"
   CHAIN_REPLY=false
   ```

   ```
   MyTarotResource
   ├ BilibiliTarot
   │ └ ……
   └ TouhouTarot
     └ ……
   ```

4. 用户应启用**至少一种主题**。仓库提供了两种主题，但仅将 `BilibiliTarot` 作为插件**内置主题**（另一主题主题可选）。配置项 `TAROT_BUILTIN_THEME_ENABLED` 以启用（默认开启）内置主题。该配置项可配合 `TAROT_EXTRA_THEMES` 使用。

   ```toml
   # 错误！无可用主题！
   TAROT_BUILTIN_THEME_ENABLED=false
   TAROT_EXTRA_THEMES=[]

   # 正确！仅使用插件内置主题 BilibiliTarot
   TAROT_BUILTIN_THEME_ENABLED=true
   TAROT_EXTRA_THEMES=[]

   # 正确！仅使用用户提供的主题 MyTarotTheme
   TAROT_BUILTIN_THEME_ENABLED=false
   TAROT_EXTRA_THEMES=["MyTarotTheme"]

   # 正确！使用插件内置主题 BilibiliTarot 与额外的主题 TouhouTarot
   TAROT_BUILTIN_THEME_ENABLED=true
   TAROT_EXTRA_THEMES=["TouhouTarot"]
   ```

5. 图片资源可选择**不部署在本地**，此时，如果所需主题为仓库提供的两种主题之一，则会尝试下载并缓存（可配置代理 `GITHUB_PROXY` ）。此外，用户也可以添加自己的塔罗牌主题。配置项 `TAROT_EXTRA_THEMES` 用以添加本地部署的自定义主题。例如，用户额外添加了两个主题，则对应目录结构为：

   ```toml
   TAROT_PATH="path-to-MyTarotResource"
   TAROT_EXTRA_THEMES=["MyTarotTheme1", "MyTarotTheme2"]
   GITHUB_PROXY="https://ghproxy.com/https://raw.githubusercontent.com/" # 或者其他代理
   ```
   ```
   MyTarotResource
   ├ MyTarotTheme1
   │ └ ……
   └ MyTarotTheme2
     └ ……
   ```

   ⚠ 默认使用 `ghproxy.com` 下载仓库内资源，不确保次次成功
   
   👉 [如何添加新的塔罗牌主题资源？](./How-to-add-new-tarot-theme.md) 欢迎贡献！🙏

## 命令

1. 启用牌阵进行占卜：[占卜]；

2. 得到单张塔罗牌回应：[塔罗牌]；

3. [超管] 群聊转发模式全局开关：[开启|启用|关闭|禁用] 群聊转发模式，可降低风控风险。

## 资源说明

1. 韦特塔罗(Waite Tarot)包括22张大阿卡纳(Major Arcana)牌与权杖(Wands)、星币(Pentacles)、圣杯(Cups)、宝剑(Swords)各系14张的小阿卡纳(Minor Arcana)共56张牌组成，其中国王、皇后、骑士、侍从也称为宫廷牌(Court Cards)；

   - BilibiliTarot：B站幻星集主题塔罗牌
   - TouhouTarot：东方主题塔罗牌，仅包含大阿卡纳

   ⚠ 资源中额外四张王牌(Ace)不在体系中，因此不会在占卜时用到，因为小阿卡纳中各系均有Ace牌，但可以自行收藏。

2. `tarot.json` 中对牌阵，抽牌张数、是否有切牌、各牌正逆位解读进行说明。`cards` 字段下对所有塔罗牌做了正逆位含义与资源路径的说明；

3. 根据牌阵的不同有不同的塔罗牌解读，同时也与问卜者的问题、占卜者的解读等因素相关，因此不存在所谓的解读方式正确与否。`cards` 字段下的正逆位含义参考以下以及其他网络资源：

   - 《棱镜/耀光塔罗牌中文翻译》，中华塔罗会馆(CNTAROT)，版权原因恕不提供
   - [AlerHugu3s/PluginVoodoo](https://github.com/AlerHugu3s/PluginVoodoo/blob/master/data/PluginVoodoo/TarotData/Tarots.json)
   - [塔罗.中国](https://tarotchina.net/)
   - [塔罗牌](http://www.taluo.org/)
   - [灵匣](https://www.lnka.cn/)

   🤔 也可以说是作者的解读版本

4. 牌面资源下载：

   - BilibiliTarot：[阿里云盘](https://www.aliyundrive.com/s/cvbxLQQ9wD5/folder/61000cc1c78a1da52ef548beb9591a01bdb09a79)

     ⚠ 文件夹名称、大阿卡纳恶魔牌(The Devil)名称、权杖4名称、女皇牌(The Empress)名称有修改

   - TouhouTarot：[Oeeder/PluginVoodoo-Touhou](https://github.com/Oeeder/PluginVoodoo-Touhou/releases/tag/PluginVoodoo)，原作：[燕山/切り絵東方タロットカード大アルカナ22枚](https://www.pixiv.net/artworks/93632047)

     ⚠ 文件名称有修改

## 本插件改自

1. [真寻bot插件库/tarot](https://github.com/AkashiCoin/nonebot_plugins_zhenxun_bot)

2. [haha114514/tarot_hoshino](https://github.com/haha114514/tarot_hoshino)
