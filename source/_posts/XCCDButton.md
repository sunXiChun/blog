---
title: "[iOS]XCCDButton"
catalog: true
toc_nav_num: true
date: 2019-01-08 10:51:24
subtitle: 
header-img: "/img/article_header/article_header3.png"
tags:
- iOS
catagories:
- iOS

---

简单的带有冷却时间的按钮

小小控件不成敬意



用法：

```

v = [[XCCDButton alloc] initWithFrame:(CGRectMake(100, 100, 100, 100))
                                  bgImage:[UIImage imageNamed:@"button_bg"]
                                maskImage:[UIImage imageNamed:@"button_shadow"]
                                 duration:3];
    
[self.view addSubview:v];
    
```

效果：


![avatar](/img/XCCDButton.gif)



[工程demo](https://github.com/sunXiChun/XCCDButton/)