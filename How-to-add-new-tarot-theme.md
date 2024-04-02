## 如何添加新的塔罗牌主题资源？

`v0.4.0` 新增东方塔罗牌主题资源！且支持用户添加主题！

1. 该功能对**图片后缀无要求**

2. 如果你有完整的塔罗牌资源，请根据[资源说明](./README.md#资源说明)与 `./resource/BilibiliTarot` 的目录结构将塔罗牌分类并**建立对应目录**，并**重命名**塔罗牌图片文件与其保持一致：

   ```python
   ["MajorArcana", "Cups", "Pentacles", "Sowrds", "Wands"]
   ```

3. 如果塔罗牌资源不完整也没关系，但请确保**每个子类资源完整**。例如，我有新的塔罗牌主题 `NewTarotTheme`，但仅有大阿卡纳22张，及圣杯15张，则建立如下 `NewTarotTheme` 子目录：

   ```
   MyTarotResource
   ├ BilibiliTarot
   │ └ ……
   └ NewTarotTheme
     ├ Cups
     │ ├ 圣杯-01.png
     │ ├ 圣杯-02.png
     │ ├ ……
     │ └ 圣杯王后.png
     └ MajorArcana
       ├ 0-愚者.png
       ├ 01-魔术师.png
       ├ ……
       └ 21-世界.png
   ```

   将其放入 `TAROT_PATH` 目录下即可。例如，上述示例中，**所有的塔罗牌资源**均在 `MyTarotResource` 目录下，则设置：

   ```toml
   TAROT_PATH="your-path-to-MyTarotResource"
   ```

   Enjoy!🥳
