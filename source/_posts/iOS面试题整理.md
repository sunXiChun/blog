---
title: "[iOS]iOS面试题整理"
catalog: true
toc_nav_num: true
date: 2021-04-21 16:13:55
subtitle: 
header-img: "/img/location_head.png"
tags:
- iOS
catagories:
- iOS

---

#### 1. 启动优化

<font color=DarkGray>
思路上是定位+解决现有问题，规范+监控后续问题。

A定位+解决现有问题
app启动分main()函数前和main()函数后。  

main()函数前，exe() -> 加载可执行文件 -> 加载Dyld -> Dyld加载动态库 -> rebase -> bind -> Objc setup -> initlalizers
Objc setup：注册ObjC类， 把category的定义插入方法列表，保证每个selector唯一
initlalizers：+load()函数，C++构造函数属性函数，非基本类型C++静态全局变量创建
1、动态库加载越多，启动越慢
2、ObjC类，方法越多，启动越慢
3、ObjC的+load()越多，启动越慢
4、C的构造函数越多，启动越慢
5、C++静态对象越多，启动越慢
美团的文章看到一种+load()优化，原来+load的操作，统一注册到一个单例里，指定位置执行。

main()函数后，分willFinishLaunchingWithOptions、didFinishLaunchingWithOptions、首页加载这几个阶段
对启动项进行分类梳理：
1、预加载，初始化等启动项、
2、不使用的类和方法、
3、同步i/o、
4、串行操作如定位到请求到渲染首页等等。
展示闪屏页面同时加载首页，把闪屏页作为App的RootViewController

B规范+监控后续问题
代码规范
Metrics性能监控系统，关键节点打上测速点
埋点系统
</font>  

#### 2. 动态库和静态库区别, 包大小有什么区别
<font color=DarkGray>
静态库：即静态链接库。以.a 为文件后缀名。在程序编译时会被链接到目标代码中，程序运行时将不再需要该静态库。
动态库：即动态链接库。以.tbd(之前叫.dylib) 为文件后缀名。linux .so windows .lib。在程序编译时并不会被链接到目标代码中，而是在程序运行是才被载入，因此在程序运行时还需要动态库存在

区别：
可执行文件大小不一样
静态链接的可执行文件要比动态链接的可执行文件要大得多，因为它将需要用到的代码从二进制文件中“拷贝”了一份，而动态库仅仅是复制了一些重定位和符号表信息。

占用磁盘大小不一样
如果有多个可执行文件，那么静态库中的同一个函数的代码就会被复制多份，而动态库只有一份，因此使用静态库占用的磁盘空间相对比动态库要大。

扩展性与兼容性不一样
如果静态库中某个函数的实现变了，那么可执行文件必须重新编译，而对于动态链接生成的可执行文件，只需要更新动态库本身即可，不需要重新编译可执行文件。正因如此，使用动态库的程序方便升级和部署。

依赖不一样
静态链接的可执行文件不需要依赖其他的内容即可运行，而动态链接的可执行文件必须依赖动态库的存在。所以如果你在安装一些软件的时候，提示某个动态库不存在的时候也就不奇怪了。
即便如此，系统中一班存在一些大量公用的库，所以使用动态库并不会有什么问题。

复杂性不一样
相对来讲，动态库的处理要比静态库要复杂，例如，如何在运行时确定地址？多个进程如何共享一个动态库？当然，作为调用者我们不需要关注。另外动态库版本的管理也是一项技术活。这也不在本文的讨论范围。

加载速度不一样
由于静态库在链接时就和可执行文件在一块了，而动态库在加载或者运行时才链接，因此，对于同样的程序，静态链接的要比动态链接加载更快。所以选择静态库还是动态库是空间和时间的考量。但是通常来说，牺牲这点性能来换取程序在空间上的节省和部署的灵活性时值得的。再加上局部性原理，牺牲的性能并不多。
</font>  

#### 3. 分类做系统方法hook操作时，有哪些注意点. 如果我的hook不想让子类和父类受影响，怎么办.
<font color=DarkGray>
没法向类中添加新的实例变量，分类没有位置容纳实例变量
存在多个同名函数的hook，调用顺序无法保证
会不会覆盖别人实现的以及继承等

参考Aspects的实现，更改当前类的isa，指向一个动态生成的中间类，内部通过当前类名决策消息转发逻辑  
https://juejin.cn/post/6844903808498319374

fishhook主要利用了共享缓存功能和PIC技术来实现hook功能。
fishHook是由faceBook开发的，是一个动态修改MachO文件的工具，主要是通过修改懒加载和非懒加载表里的指针的指向来达到hook的目的，因此一般用它来hook系统的C函数。
https://blog.csdn.net/Hello_Hwc/article/details/78444203
</font> 

#### 4. autoReleasePool原理
<font color=DarkGray>
AutoreleasePool（自动释放池）是OC中的一种内存自动回收机制，
在正常情况下，创建的变量会在超出其作用域的时候release，但是如果将变量加入AutoreleasePool，那么release将延迟执行。

Autorelease Pool的本质上是一个双向链表。双向链表中每一页为一个AutoreleasePoolPage，AutoreleasePoolPage最大为4096B，每当AutoreleasePoolPage中因为存储变量总大小超过4096B之后，就会分配一个新的AutoreleasePoolPage

objc_autoreleasePoolPush()
每个 AutoreleasePoolPage 对象会开启 4096字节（4kb）内存，除了自身实例变量所占空间，剩下的空间全部拿来存储 autorelease 对象的地址。

每当进行一次 objc_autoreleasePoolPush 调用时，runtime 都会向当前的 AutoreleasePoolPage 中添加一个哨兵对象，值为 nil，
添加完哨兵对象后，将 next 指针指向下一个添加 Autorelease 对象的位置。当当前 AutoreleasePoolPage 满了，开启一个新的 AutoreleasePoolPage，并更新 child 和 parent 指针，以组成双向链表。

objc_autoreleasePoolPop()
objc_autoreleasePoolPush 会有个返回值，这个返回值正是前面提到的哨兵对象。objc_autoreleasePoolPop() 调用时会把哨兵对象作为入参。之后根据传入的哨兵对象地址找到哨兵对象对应的 AutoreleasePoolPage；在当前 page 中，对所有晚于哨兵对象插入的 Autorelease 对象发送 release 消息，到哨兵对象后，销毁当前 page；再根据 parent 向前继续进行 pop，知道第一个哨兵对象所在 page 释放完成。

App 启动后，苹果在主线程 RunLoop 里注册了两个 Observer，其回调都是 _wrapRunLoopWithAutoreleasePoolHandler()。

第一个 Observer 监视的事件是 Entry(即将进入 Loop)，其回调内会调用 _objc_autoreleasePoolPush() 创建自动释放池。其 order 是 -2147483647，优先级最高，保证创建释放池发生在其他所有回调之前。

第二个 Observer 监视了两个事件：BeforeWaiting(准备进入休眠) 时调用 _objc_autoreleasePoolPop() 和 _objc_autoreleasePoolPush() 释放旧的池并创建新池；Exit(即将退出Loop) 时调用 _objc_autoreleasePoolPop() 来释放自动释放池。这个 Observer 的 order 是 2147483647，优先级最低，保证其释放池子发生在其他所有回调之后。

alloc/new/copy/mutableCopy等持有对象的方法，不会加入 autoreleasePool；其他不持有对象的方法通过 objc_autoreleaseReturnValue 和 objc_retainAutoreleasedReturnValue 来判断是否需要加入 autoreleasePool，这是编译器的优化。

iOS5 及之前的编译器，关键字 __weak 修饰的对象，会自动加入 autoreleasePool；iOS5 及之后的编译器，则直接调用的 release，不会加入 autoreleasePool。

id 指针(id *)和对象指针（NSError **），会自动加上关键字 __autorealeasing，加入 autoreleasePool。

https://blog.jonyfang.com/2018/06/12/2018-06-12-objc-autoreleasePool/

</font> 

#### 5. LRU缓存算法实现原理, 为什么是双向链表, 如何快速找到某一个对象.
<font color=DarkGray>
新数据直接插入到列表头部,缓存数据被命中，将数据移动到列表头部,缓存已满的时候，移除列表尾部数据。

为什么是双向链表：需要知道中间节点前一个节点的信息，单向链表就不得不再次遍历获取信息

TTMemeryCache LRU实现 双向链表+dic
直接去dic里取对象

hashmap + 双向链表 根据key计算索引找到对象

Redis 更加高效 局部回收缓存池16个元素数组，随机取5个，对比空闲时间最大的存入数组，淘汰时从尾部淘汰。
</font> 

#### 6. 模块化实现思想
<font color=DarkGray>
单一业务划分，业务解耦，独立维护和测试，提高团队合作效率

模块划分
基础层、中间层、业务层。
基础层模块比如像网络框架、持久化、Log、社交化分享这样的模块，具有很强的可重用性。
中间层模块可以有登录模块、网络层、资源模块等，它们依赖着基础组件但又没有很强的业务属性，同时业务层对这层模块的依赖是很强的。
业务层模块，比如类似朋友圈、直播、Feeds流这样的业务功能了。

代码隔离
模块化首先要做的是代码层面上独立，任意一个基础模块都是可以独立编译的，底层模块绝对不能有对上层模块的代码依赖。
在这里我们选择使用CocoaPods来确保模块间代码隔离，私有pods组件。

依赖管理
依赖的版本管理，IKBaseSDK

模块集成
一般来说，模块初始化需要在APP启动或者UI初始化附近的时机来完成，有时候各个模块的启动顺序可能也是有讲究的。配合启动优化，分willFinishLaunchingWithOptions、didFinishLaunchingWithOptions、首页几种时机进行初始化。

App生命周期事件
在各个生命周期调用IKMoudleCenter，分发给各个组件。

通信
通知、代理、消息注册机制
复杂对象传输，json方案

</font> 

#### 7. block的底层实现，栈block和堆block区别,为什么会循环引用,为什么__weak修饰后能解决.
<font color=DarkGray>
</font> 

#### 8. weak指针实现原理.  哈希表如果冲突怎么办.  对象在销毁时，如果存在哈希冲突，如何能正确找到对的weak指针.
<font color=DarkGray>
</font> 

#### 9. 分类和扩展区别
<font color=DarkGray>
Extension 在编译期决定，它就是类的一部分，在编译期和头文件里的 @interface 以及实现文件里的 @implement 一起形成一个完整的类，它伴随类的产生而产生，亦随之一起消亡。Extension 一般用来隐藏类的私有信息，你必须有一个类才能为这个类添加 Extension，所以你无法为系统的类比如 NSString 添加 Extension。

Category 则完全不一样，它是在运行期决议的。

Extension 可以添加成员变量，而 Category 是无法添加成员变量的。因为 Category 在运行期，对象的内存布局已经确定，如果添加实例变量就会破坏类的内部布局。

https://tech.meituan.com/2015/03/03/diveintocategory.html
</font> 

#### 10. 为什么分类不能添加成员变量
<font color=DarkGray>
</font> 

#### 11. 关联属性加的成员变量什么时机释放，怎么判断对象有没有关联属性
<font color=DarkGray>
</font> 

#### 12. dispatch_once实现原理, 如何保证一段代码只执行一次
<font color=DarkGray>
</font> 

#### 13. 什么是属性，属性与成员变量的区别，如果属性和成员变量同名，如何实现两个不同的
<font color=DarkGray>
</font> 

#### 14. 事件传递和响应机制，查找的顺序，问到pointInside:withEvent
<font color=DarkGray>
</font> 

#### 15. 内存管理，创建的局部变量释放进机，有哪种情况会被加到autoreleasepool延迟释放
<font color=DarkGray>
</font> 

#### 16. kvo原理，会问到isa指针指向派生类
<font color=DarkGray>
</font> 

#### 17. 数据集合线程锁的问题，实现单写多读
<font color=DarkGray>
</font> 

#### 18. weak属性的原理，会问到key和value存放的和关系等，
<font color=DarkGray>
</font> 

#### 19. 内存的生命周期，内存的释放原理，内存有没有自动释放的可能，内存自动释放的情况有几种，（类方法可以延迟释放缓存）
<font color=DarkGray>
</font> 

#### 20. 线程锁
<font color=DarkGray>
</font> 

#### 21. 响应链
<font color=DarkGray>
</font> 

#### 22. KAO的原理
<font color=DarkGray>
</font> 

#### 23. 算法：判断回文字符串，两种方法：数组和链表， 链表会问到是否奇数和偶数的边界问题
<font color=DarkGray>
</font> 

#### 关于id CLASS , SEL, IMP的说明
<font color=DarkGray>
id就是一种动态类型，它可以指向属于任何继承与NSObject类的对象，这样id就可以调用项目中所有继承与NSObject类的方法（但可能调用的方法不在对象中，要小心使用）
id 是一个结构体指针类型:
typedef struct objc_object *id {
    Class isa;
};

Class是一个结构体指针类型
typedef struct objc_class *Class {
  	Class isa  OBJC_ISA_AVAILABILITY;

#if !__OBJC2__
    Class super_class                                        OBJC2_UNAVAILABLE;
    const char *name                                         OBJC2_UNAVAILABLE;
    long version                                             OBJC2_UNAVAILABLE;
    long info                                                OBJC2_UNAVAILABLE;
    long instance_size                                       OBJC2_UNAVAILABLE;
    struct objc_ivar_list *ivars                             OBJC2_UNAVAILABLE;
    struct objc_method_list **methodLists                    OBJC2_UNAVAILABLE;
    struct objc_cache *cache                                 OBJC2_UNAVAILABLE;
    struct objc_protocol_list *protocols                     OBJC2_UNAVAILABLE;
#endif
};

SEL是一个结构体指针类型，也就是selector，指向objc_selector结构体的指针， selector 是一个已被Objective-C运行时注册过或映射过的C语言字符串， 如果想创建 selector ，必须使用 sel_registername 的返回值或者编译器指令@selector()

IMP(implement)实际上是一个函数指针，指向方法实现的首地址。代表了方法的最终实现。

https://blog.csdn.net/BoilerUp/article/details/109440485

</font> 


#### 里达大神推荐
<font color=DarkGray>
https://tech.meituan.com/2018/12/06/waimai-ios-optimizing-startup.html
https://blog.ibireme.com/2015/05/18/runloop/
</font> 

