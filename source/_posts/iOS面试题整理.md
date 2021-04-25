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

block本质上是一个OC对象，它内部也有isa指针，这个对象封装了函数调用地址以及函数调用环境(函数参数、返回值、捕获的外部变量等)
</font> 

```
struct __main_block_impl_0 {
    struct __block_impl impl;
    struct __main_block_desc_0 *Desc;
    int age;
}
```

<font color=DarkGray>
impl中存放的isa，FuncPtr是block要执行的函数指针。
Desc存放的block占用的内存大小
age，捕获的外部变量

变量捕获
全局变量 - 不会捕获，直接访问
静态局部变量 - 捕获地址
普通局部变量 - 捕获变量的值

__NSGlobalBlock__
block里面没有访问普通局部变量(也就是说block里面没有访问任何外部变量或者访问的是静态局部变量或者访问的是全局变量)
在内存中是存在数据区的，调用copy方法的话什么都不会做
继承自NSObject，__NSGlobalBlock__的继承链为：__NSGlobalBlock__ : __NSGlobalBlock : NSBlock : NSObject

__NSStackBlock__
里面访问了普通的局部变量，
在内存中存储在栈区，做copy操作，那会将这个block从栈复制到堆上
继承链是：__NSStackBlock__ : __NSStackBlock : NSBlock : NSObject

__NSMallocBlock__
是存储在堆区
做copy操作，那这个block的引用计数+1
ARC环境下，编译器会根据情况，自动将栈上的block复制到堆上
a. block作为函数返回值时
b. 将block赋值给强指针时
c. 当block作为参数传给Cocoa API时
d. block作为GCD的API的参数时
在MRC环境下，定义block属性建议使用copy关键字，这样会将栈区的block复制到堆区
在ARC环境下，定义block属性用copy或strong关键字都会将栈区block复制到堆上，所以这两种写法都可以

当block被拷贝到堆上时是调用的copy函数，copy函数内部会调用_Block_object_assign函数，_Block_object_assign函数就会根据这3个关键字来进行操作。

如果关键字是__strong，那block内部就会对这个对象进行一次retain操作，引用计数+1，也就是block会强引用这个对象。也正是这个原因，导致在使用block时很容易造成循环引用。
如果关键字是__weak或__unsafe_unretained，那block对这个对象是弱引用，不会造成循环引用。所以我们通常在block外面定义一个__weak或__unsafe_unretained修饰的弱指针指向对象，然后在block内部使用这个弱指针来解决循环引用的问题。
block从堆上移除时，则会调用block内部的dispose函数，dispose函数内部调用_Block_object_dispose函数会自动释放强引用的变量。
</font> 

```
// 底层结构体
struct __main_block_impl_0 {
  struct __block_impl impl;
  struct __main_block_desc_0* Desc;
  Person *__strong person;
};

// 底层block
struct __main_block_impl_0 {
  struct __block_impl impl;
  struct __main_block_desc_0* Desc;
  Person *__weak weakPerson;
};

__block：
struct __main_block_impl_0 {
  struct __block_impl impl;
  struct __main_block_desc_0* Desc;
  __Block_byref_age_0 *age; // by ref
};

struct __Block_byref_age_0 {
  void *__isa; // isa指针
__Block_byref_age_0 *__forwarding; // 如果这block是在堆上那么这个指针就是指向它自己，如果这个block是在栈上，那这个指针是指向它拷贝到堆上后的那个block
 int __flags;
 int __size; // 结构体大小
 int age; // 真正捕获到的age
};
```

<font color=DarkGray>
__block不管是修饰基础数据类型还是修饰对象数据类型，底层都是将它包装成一个对象(我这里取个名字叫__blockObj)，然后block结构体中有个指针指向__blockObj
当block在栈上时，block内部并不会对__blockObj产生强引用
当block调用copy函数从栈拷贝到堆中时，它同时会将__blockObj也拷贝到堆上，并对__blockObj产生强引用
当block从堆中移除时，会调用block内部的dispose函数，dispose函数内部又会调用_Block_object_dispose函数来释放__blockObj

https://www.jianshu.com/p/8de36c7e3440
</font> 

#### 8. weak指针实现原理.  哈希表如果冲突怎么办.  对象在销毁时，如果存在哈希冲突，如何能正确找到对的weak指针.
<font color=DarkGray>
__weak和__unsafe_unretained的区别就是前者会在对象被释放的时候自动置为nil，而后者却不行

当一个对象obj被weak指针指向时，这个weak指针会以obj作为key，被存储到sideTable类的weak_table这个散列表上对应的一个weak指针数组里面。
当一个对象obj的dealloc方法被调用时，Runtime会以obj为key，从sideTable的weak_table散列表中，找出对应的weak指针列表，然后将里面的weak指针逐个置为nil。

SideTables是一个64个元素长度的hash数组，里面存储了SideTable。SideTables的hash键值就是一个对象obj的address
每一个 SideTable 又包含有一个自选锁、一张全局的引用计数表、一张全局的弱引用表
</font> 

```
struct SideTable {
    spinlock_t slock;           // 自旋锁，防止多线程访问冲突
    RefcountMap refcnts;        // 对象引用计数map
    weak_table_t weak_table;    // 对象弱引用map
};
```

<font color=DarkGray>
所有对象对应的SideTable。都存储在一个全局变量SideTableBuf中
StripedMap<SideTable>类其实是包装了一个结构体的成员变量array的哈希表
当系统调用 SideTables()[对象指针]时，StripedMap<SideTable>这个哈希表就会在array中找出对应数组指针的SideTable类返回，这里可以看出其中的一个SideTable类变量可能对应多个不同的对象指针。

SideTable是不能被析构的

当引用计数大于无法使用位存储时，也会创建sidetable，并使用sidetable进行引用计数。同时objc_initWeak也是创建sidetable
</font> 


```
# if __arm64__
#   define ISA_MASK        0x0000000ffffffff8ULL
#   define ISA_MAGIC_MASK  0x000003f000000001ULL
#   define ISA_MAGIC_VALUE 0x000001a000000001ULL
    struct {
        uintptr_t nonpointer        : 1;
        uintptr_t has_assoc         : 1; //有关联的对象
        uintptr_t has_cxx_dtor      : 1; //c++ 析构
        uintptr_t shiftcls          : 33; // MACH_VM_MAX_ADDRESS 0x1000000000
        uintptr_t magic             : 6; //判断当前对象是真的对象还是没有初始化的空间
        uintptr_t weakly_referenced : 1;
        uintptr_t deallocating      : 1;
        uintptr_t has_sidetable_rc  : 1; //是否有sidetable引用计数
        uintptr_t extra_rc          : 19; //引用计数
#       define RC_ONE   (1ULL<<45)
#       define RC_HALF  (1ULL<<18)
    };

```

has_sidetable_rc即表示是否有sidetable进行引用计数

```
struct SideTable {
    spinlock_t slock;
    RefcountMap refcnts;
    weak_table_t weak_table;
};

struct weak_table_t {
    weak_entry_t *weak_entries;
    size_t    num_entries;
    uintptr_t mask;
    uintptr_t max_hash_displacement;
};

struct weak_entry_t {
    DisguisedPtr<objc_object> referent;
    union {
        struct {
            weak_referrer_t *referrers;
            uintptr_t        out_of_line_ness : 2;
            uintptr_t        num_refs : PTR_MINUS_2;
            uintptr_t        mask;
            uintptr_t        max_hash_displacement;
        };
        struct {
            // out_of_line_ness field is low bits of inline_referrers[1]
            weak_referrer_t  inline_referrers[WEAK_INLINE_COUNT];
        };
    };
    ......
}
```

weak_entry_t大于3/4进行扩容，weak_resize。


dealloc里 __weak self 崩溃
```
id weak_register_no_lock(weak_table_t *weak_table, id referent_id, 
                      id *referrer_id, WeakRegisterDeallocatingOptions deallocatingOptions){
.....
        if (deallocating) {
            if (deallocatingOptions == CrashIfDeallocating) {
                _objc_fatal("Cannot form weak reference to instance (%p) of "
                            "class %s. It is possible that this object was "
                            "over-released, or is in the process of deallocation.",
                            (void*)referent, object_getClassName((id)referent));
            } else {
                return nil;
            }
        }
.....
}
```

dealloc方法最终会走向rootDealloc
```
inline void
objc_object::rootDealloc()
{
    if (isTaggedPointer()) return;  // fixme necessary?

    if (fastpath(isa.nonpointer  &&   //为1表示优化后的isa即isa_t
                 !isa.weakly_referenced  &&   //无弱引用,不需要释放sidetable
                 !isa.has_assoc  &&   //无关联属性，例如分类中添加的
                 !isa.has_cxx_dtor  &&  //不需要调用c++析构方法
                 !isa.has_sidetable_rc)) //无sidetable引用计数
    {
        assert(!sidetable_present());
        free(this);
    } 
    else {
        object_dispose((id)this); //正常释放
    }
}
```

object_dispose最终会跳转到
```
/***********************************************************************
* objc_destructInstance
* Destroys an instance without freeing memory. 
* Calls C++ destructors.
* Calls ARC ivar cleanup.
* Removes associative references.
* Returns `obj`. Does nothing if `obj` is nil.
**********************************************************************/
void *objc_destructInstance(id obj) 
{
    if (obj) {
        // Read all of the flags at once for performance.
        bool cxx = obj->hasCxxDtor();
        bool assoc = obj->hasAssociatedObjects();

        // This order is important.
        if (cxx) object_cxxDestruct(obj); //c++析构函数调用
        if (assoc) _object_remove_assocations(obj); //关联对象移除 是一个hash表
        obj->clearDeallocating(); //这里进行弱引用表sidetable的相关释放操作，包括表的释放以及引用计数
    }

    return obj;
}

inline void 
objc_object::clearDeallocating()
{
    if (slowpath(!isa.nonpointer)) {
        // Slow path for raw pointer isa.
        sidetable_clearDeallocating();
    }
    else if (slowpath(isa.weakly_referenced  ||  isa.has_sidetable_rc)) {
        // Slow path for non-pointer isa with weak refs and/or side table data.
        clearDeallocating_slow();
    }

    assert(!sidetable_present());
}

// Slow path of clearDeallocating() 
// for objects with nonpointer isa
// that were ever weakly referenced 
// or whose retain count ever overflowed to the side table.
NEVER_INLINE void
objc_object::clearDeallocating_slow()
{
    assert(isa.nonpointer  &&  (isa.weakly_referenced || isa.has_sidetable_rc));

    SideTable& table = SideTables()[this];
    table.lock();
    if (isa.weakly_referenced) {
        weak_clear_no_lock(&table.weak_table, (id)this);
    }
    if (isa.has_sidetable_rc) {
        table.refcnts.erase(this);
    }
    table.unlock();
}

#endif
```

<font color=DarkGray>
所以dealloc包括以下几个步骤

1、c++析构函数调用
2、关联对象(例如使用runtime在分类中关联变量)移除，是一个hash表来存储
3、这里进行弱引用表sidetable的相关释放操作，包括表的释放以及引用计数，即weak指针置为nil的操作就在这里
值得注意的是dealloc方法是对象引用计数在哪个线程为0，则在哪个线程调用dealloc方法，所以不一定在主线程执行

https://blog.csdn.net/shengpeng3344/article/details/105825715


</font> 

#### 关联对象
<font color=DarkGray>
objc_setAssociatedObject(id object, const void *key, id value, objc_AssociationPolicy policy);
</font> 

```
全局AssociationsManager
-----AssociationsHashMap
----------DISGUISE(object):ObjectAssociationMap
--------------------key:ObjcAssociation 对象(存储 policy,value)
```

<font color=DarkGray>
AssociationsManager里边有个 spinlock_t锁 对 _map 这个全局唯一的实例 进行加锁和解锁

AssociationsHashMap 类似于 OC 的 NSDictionary ,其中用 disguised_ptr_t 作为 key ,ObjectAssociationMap * 作为一个 value
disguised_ptr_t 是  uintptr_t 的类型
intptr_t 和uintptr_t 类型用来存放指针地址。它们提供了一种可移植且安全的方法声明指针，而且和系统中使用的指针长度相同，对于把指针转化成整数形式来说很有用。
可以把disguised_ptr_t理解为一个指针类型的变量

关联对象并不是存储在被关联对象本身内存中，而是存储在全局的统一的一个AssociationsManager中，如果设置关联对象为nil，就相当于是移除关联对象。

</font> 

#### Notification
<font color=DarkGray>
NSNotificationCenter中定义了两个Table，同时为了封装观察者信息，也定义了一个Observation保存观察者信息。他们的结构体可以简化如下
</font> 

```
typedef struct NCTbl {
  Observation   *wildcard;  /* 保存既没有没有传入通知名字也没有传入object的通知*/
 MapTable       nameless;   /*保存没有传入通知名字的通知 */
 MapTable       named; /*保存传入了通知名字的通知 */
} NCTable;

typedef struct  Obs {
  id        observer;   /* 保存接受消息的对象*/
  SEL       selector;   /* 保存注册通知时传入的SEL*/
  struct Obs    *next;      /* 保存注册了同一个通知的下一个观察者*/
  struct NCTbl  *link;  /* 保存改Observation的Table*/
} Observation;

Named Table
--Key：Table
------Object：单向链表（Observer-Observer-Observer-Observer）

nameless Table
--Object：单向链表（Observer-Observer-Observer-Observer）
```

<font color=DarkGray>
如果在注册观察者的时候既没有NotifcationName，同时没有传入Object。经过代码实践，所有的系统通知都会发送到注册的对象这里。恰恰对应到上面提到的数据结构中的wildcard字段。

[observerNode->observer performSelector: o->selector withObject: notification];

通知的定义最好统一放在一个头文件中定义好，命名也尽量规范。
接收通知的线程，和发送通知所处的线程是同一个线程。如果要接收通知更新UI，注意发送通知的线程是否为主线程。

NSNotificationQueue
通知队列，用于异步发送消息，这个异步并不是开启线程，而是把通知存到双向链表实现的队列里面，等待某个时机触发时调用NSNotificationCenter的发送接口进行发送通知

NSNotificationQueue是依赖runloop的，所以如果线程的runloop未开启则无效
</font> 

```
NSNotification *notification = [NSNotification notificationWithName:kNotificationName
                                                                     object:@"object"];
[[NSNotificationQueue defaultQueue] enqueueNotification:notification postingStyle:NSPostASAP]

- (void)enqueueNotification:(NSNotification *)notification postingStyle:(NSPostingStyle)postingStyle coalesceMask:(NSNotificationCoalescing)coalesceMask forModes:(nullable NSArray<NSRunLoopMode> *)modes;

typedef NS_ENUM(NSUInteger, NSPostingStyle) {
    NSPostWhenIdle = 1, //runloop空闲时发送
    NSPostASAP = 2,     //当前通知或者timer的回调执行完毕时发送
    NSPostNow = 3       //多个相同的通知合并之后马上发送
};

typedef NS_OPTIONS(NSUInteger, NSNotificationCoalescing) {
    NSNotificationNoCoalescing = 0,         //不管是否重复，不合并
    NSNotificationCoalescingOnName = 1,     //按照通知的名字
    NSNotificationCoalescingOnSender = 2    //按照发送方
};
```

<font color=DarkGray>
需要注意的是，当NSPostingStyle的类型是NSPostWhenIdle和NSPostASAP时确实是异步的，而当类型是NSPostNow时则是同步的

*子线程post 主线程接收事件：
NSPort *myPort = [NSMachPort port];
myPort.delegate = self;
[[NSRunLoop currentRunLoop] addPort:myPort forMode:NSDefaultRunLoopMode];

[myPort sendBeforeDate:[NSDate date] msgid:100 components:nil from:nil reserved:0];

https://cloud.tencent.com/developer/article/1445968

</font> 

#### kvo实现原理
<font color=DarkGray>
KVO主要用来做键值观察操作，想要一个值发生改变后通知另一个对象，则用KVO实现最为合适

KVO在属性发生改变时的调用是自动的

如果想要手动控制
[self willChangeValueForKey:@"balance"];
_balance = theBalance;
[self didChangeValueForKey:@"balance"];

如果想控制当前对象的自动调用过程
+ (BOOL)automaticallyNotifiesObserversForKey:(NSString *)theKey {
    BOOL automatic = NO;
    if ([theKey isEqualToString:@"balance"]) {
        automatic = NO;
    }
    else {
        automatic = [super automaticallyNotifiesObserversForKey:theKey];
    }
    return automatic;
}

KVO是通过isa-swizzling技术实现的(这句话是整个KVO实现的重点)。在运行时根据原类创建一个中间类，这个中间类是原类的子类，并动态修改当前对象的isa指向中间类。并且将class方法重写，返回原类的Class。所以苹果建议在开发中不应该依赖isa指针，而是通过class实例方法来获取对象类型。

对象被KVO后，其真正类型变为了NSKVONotifying_KVOObject类，已经不是之前的类了。
KVO会在运行时动态创建一个新类，将对象的isa指向新创建的类，新类是原类的子类，命名规则是NSKVONotifying_xxx的格式。
KVO为了使其更像之前的类，还会将对象的class实例方法重写，使其更像原类
_isKVOA方法可以当做使用了KVO的一个标记。如果我们想判断当前类是否是KVO动态生成的类，就可以从方法列表中搜索这个方法。

KVO会重写keyPath对应属性的setter方法，没有被KVO的属性则不会重写其setter方法
在重写的setter方法中，修改值之前会调用willChangeValueForKey:方法，修改值之后会调用didChangeValueForKey:方法，这两个方法最终都会被调用到observeValueForKeyPath:ofObject:change:context:方法中

KVO是一种事件绑定机制的实现，在keyPath对应的值发生改变后会回调对应的方法。
这种数据绑定机制，在对象关系很复杂的情况下，很容易导致不好排查的bug。例如keyPath对应的属性被调用的关系很复杂，就不太建议对这个属性进行KVO
KVO还不支持block语法

自己实现KVO
https://www.jianshu.com/p/945a196e16b0

Facebook的一个KVO开源第三方框架-KVOController

FBKVOController *KVOController = [FBKVOController controllerWithObserver:self];
[KVOController observe:clock keyPath:@"date" options:NSKeyValueObservingOptionInitial|NSKeyValueObservingOptionNew block:^(ClockView *clockView, Clock *clock, NSDictionary *change) {
  clockView.date = change[NSKeyValueChangeNewKey];
}];

可以同时对一个对象的多个属性进行监听，写法简洁；
通知不会向已释放的观察者发送消息；
增加了block和自定义操作对NSKeyValueObserving回调的处理支持；
不需要在dealloc 方法中手动移除观察者，而且移除观察者不会抛出异常，当FBKVOController对象被释放时， 观察者被隐式移除；

_FBKVOInfo NSMapTable
_FBKVOSharedController 向完成真正的观察者注册

使用FBKVOController的话，不需要手动调用removeObserver方法，在被监听对象消失的时候，会在dealloc中调用remove方法。如果因为业务需求，可以手动调用remove方法，重复调用remove方法不会有问题


</font> 

#### kvc实现原理
<font color=DarkGray>
KVC是Key Value Coding的简称。它是一种可以通过字符串的名字（key）来访问类属性的机制。
我们经常用KVC或者setter方法来触发KVO，实现键值变化监听，实现一些功能。

// 1、将键字符串key所对应的属性的值设置为value。不能设定属性值时，将会引起接收器调用方法2
- (void)setValue:(nullable id)value forKey:(NSString *)key

// 2、当属性值设置失败，调用此方法
- (void)setValue:(nullable id)value forUndefinedKey:(NSString *)key

// 3、返回标识属性的键字符串所对应的值。如果获取失败，将会引起接收器调用方法4
- (nullable id)valueForKey:(NSString *)key

// 4、取值失败，调用此方法
- (nullable id)valueForUndefinedKey:(NSString *)key

// 5、在键字符串key所对应的"标量"型属性值设为nil，调用此方法，并抛出NSInvalidArgumentException异常(可demo测试)
- (void)setNilValueForKey:(NSString *)key


// 6、默认返回值YES，代表如果没有找到Set方法的话，会按照_key，_iskey，key，iskey的顺序搜索成员，设置成NO就不这样搜索
+ (BOOL)accessInstanceVariablesDirectly

赋值实现原理
首先会按照setKey、_setKey的顺序查找方法，找到方法，直接调用方法并赋值；
未找到方法，则调用+ (BOOL)accessInstanceVariablesDirectly;
若accessInstanceVariablesDirectly方法返回YES，则按照_key、_isKey、key、isKey的顺序查找成员变量，找到直接赋值，找不到则抛出异常；
若accessInstanceVariablesDirectly方法返回NO，则直接抛出异常； 

取值实现原理
首先会按照getKey、key、isKey、_key的顺序查找方法，找到直接调用取值
若未找到，则查看+ (BOOL)accessInstanceVariablesDirectly的返回值，若返回NO，则直接抛出异常；
若返回的YES，则按照_key、_isKey、key、isKey的顺序查找成员变量，找到则取值；
找不到则抛出异常；

相关面试题
1、iOS用什么方式实现对一个对象的KVO?(KVO的本质是什么？）
利用RuntimeAPI动态生成一个子类，并且让instance对象的isa指向这个全新的子类；
当修改instance对象的属性时，会调用Foundation的_NSSetXXXValueAndNotify函数
先调用willChangeValueForKey；
接着调用父类原来的setter方法；
最后调用didChangeValueForKey，其内部会触发监听器（Oberser)的监听方法（observerValueForKeyPath:ofObject:change:context:);

2、如何手动触发KVO?
手动调用willChangeValueForKey： 和 didChangeValueForKey:

3、直接修改成员变量会触发KVO么？
不会触发KVO

4、通过KVC修改属性会触发KVO么？
会触发KVO，KVC在修改属性时，会调用willChangeValueForKey： 和 didChangeValueForKey:方法；


</font> 

#### 9. 分类和扩展区别
<font color=DarkGray>

分类中只能添加“方法”，不能增加成员变量。
分类中可以访问原来类中的成员变量，但是只能访问@protect和@public形式的变量。如果想要访问本类中的私有变量，分类和子类一样，只能通过方法来访问。
如果一定要在分类中添加成员变量，可以通过getter，setter手段进行添加

在本类和分类有相同的方法时，优先调用分类的方法再调用本类的方法 
如果有两个分类，他们都实现了相同的方法，如何判断谁先执行？分类执行顺序可以通过targets,Build Phases,Complie Source进行调节，注意执行顺序是从上到下的


扩展其实就是分类的一个特例，就是没有名字，匿名的分类就是扩展，由于是在.m文件中声明的分类，所以是优化的，外面是看不到
扩展中可以声明实例变量，可以声明属性
通常定义在主类的.m文件中，所以扩展声明的方法和属性通常是私有的

分类和扩展的区别
1、分类是不可以声明实例变量，扩展是可以声明实例变量，是私有的
2、扩展是在编译阶段被添加到类中，而分类是在运行时添加到类中
3、扩展不能像分类那样拥有独立的实现部分（@implementation部分），和本类共享一个实现。也就是说，扩展所声明的方法必须依托对应宿主类的实现部分来实现

如果分类中有和原有类同名的方法，会优先调用分类中的方法，就是说会忽略原有类的方法。所以同名方法调用的优先级为：分类>本类>父类

category其实并不是完全替换掉原来类的同名方法，只是category在方法列表的前面而已，所以我们只要顺着方法列表找到最后一个对应名字的方法，就可以调用原来类的方法：

https://tech.meituan.com/2015/03/03/diveintocategory.html
</font> 

#### 方法缓存
<font color=DarkGray>
方法缓存存在什么地方？
类的定义里就有cache字段，类的所有缓存都存在metaclass上，所以每个类都只有一份方法缓存

父类方法的缓存只存在父类么，还是子类也会缓存父类的方法？
从父类取到的方法，也会存在类本身的方法缓存里。而当用一个父类对象去调用那个方法的时候，也会在父类的metaclass里缓存一份。

类的方法缓存大小有没有限制？
散列表特性，方法缓存第奇数次满（使用的槽位超过3/4）的时候，方法缓存的大小才会增长。当第偶数次满的时候，方法缓存会被清空并重新利用。
答案是没有限制，虽然这个值被设置为1，方法缓存的大小增速会慢一点，但是确实是没有上限的。

为什么类的方法列表不直接做成散列表呢，做成list，还要单独缓存，多费事？
散列表是没有顺序的，Objective-C的方法列表是一个list，是有顺序的；Objective-C在查找方法的时候会顺着list依次寻找，并且category的方法在原始方法list的前面，需要先被找到，如果直接用hash存方法，方法的顺序就没法保证。
list的方法还保存了除了selector和imp之外其他很多属性
散列表是有空槽的，会浪费空间


</font> 

#### 10. 为什么分类不能添加成员变量
<font color=DarkGray>

Objective-C类是由Class类型来表示的，它实际上是一个指向objc_class结构体的指针。它的定义如下：

typedef struct objc_class *Class;

objc_class结构体的定义如下：

</font> 

```
struct objc_class{
    Class isa  OBJC_ISA_AVAILABILITY;
    #if!__OBJC2__Class super_class                      
    OBJC2_UNAVAILABLE;// 父类constchar*name                        
    OBJC2_UNAVAILABLE;// 类名longversion                            
    OBJC2_UNAVAILABLE;// 类的版本信息，默认为0longinfo                              OBJC2_UNAVAILABLE;// 类信息，供运行期使用的一些位标识longinstance_size                      OBJC2_UNAVAILABLE;// 该类的实例变量大小

    struct objc_ivar_list *ivars OBJC2_UNAVAILABLE;// 该类的成员变量链表
    struct objc_method_list **methodLists OBJC2_UNAVAILABLE;// 方法定义的链表
    struct objc_cache *cacheOBJC2_UNAVAILABLE;// 方法缓存
    struct objc_protocol_list *protocols OBJC2_UNAVAILABLE;// 协议链表#endif
} OBJC2_UNAVAILABLE;

```

<font color=DarkGray>
在上面的objc_class结构体中，
ivars是objc_ivar_list（成员变量列表）指针；
methodLists是指向objc_method_list指针的指针。

在Runtime中，objc_class结构体大小是固定的，不可能往这个结构体中添加数据，只能修改。所以ivars指向的是一个固定区域，只能修改成员变量值，不能增加成员变量个数。
methodList是一个二维数组，所以可以修改*methodLists的值来增加成员方法，虽没办法扩展methodLists指向的内存区域，却可以改变这个内存区域的值（存储的是指针）。因此，可以动态添加方法，不能添加成员变量。

在Objective-C提供的runtime函数中，确实有一个class_addIvar()函数用于给类添加成员变量，但是文档中特别说明：

This function may only be called after objc_allocateClassPair and before objc_registerClassPair. Adding an instance variable to an existing class is not supported.

意思是说，这个函数只能在“构建一个类的过程中”调用。一旦完成类定义，就不能再添加成员变量了。经过编译的类在程序启动后就runtime加载，没有机会调用addIvar。程序在运行时动态构建的类需要在调用objc_allocateClassPair之后，objc_registerClassPair之前才可以被使用，同样没有机会再添加成员变量。


Category不能添加成员变量（instance variables），那到底能不能添加属性（property）呢？
Category的结构体
</font> 

```
typedef struct category_t {
    const char *name;//类的名字
    classref _tcls;//类
    struct method_list_t *instanceMethods;//category中所有给类添加的实例方法的列表
    struct method_list_t *classMethods;//category中所有添加的类方法的列表
    struct protocol_list_t *protocols;//category实现的所有协议的列表
    struct property_list_t *instanceProperties;//category中添加的所有属性
}category_t;
```

<font color=DarkGray>
从Category的定义也可以看出Category可以添加实例方法，类方法，甚至可以实现协议，添加属性 无法添加实例变量

那我们为什么经常听说说类别不能添加属性呢？
实际上，Category实际上允许添加属性的，同样可以使用@property，但是不会生成_变量（带下划线的成员变量），也不会生成添加属性的getter和setter方法，所以，尽管添加了属性，也无法使用点语法调用getter和setter方法

https://www.jianshu.com/p/e203d70ccc3f
</font> 

#### 11. 关联属性加的成员变量什么时机释放，怎么判断对象有没有关联属性
<font color=DarkGray>
底层使用AssociationsManager统一管理各个对象的 associated objects关联对象.然后通过static key(一般是一个固定值)去访问对应的associated object关联对象.然后在dealloc的时候调用擦除函数(associations.erase())来解除对这些关联对象的引用:
</font> 

```
dealloc
    object_dispose
        objc_destructInstance
            _object_remove_assocations 
```

<font color=DarkGray>
isa.has_assoc 有没有关联属性

</font> 

#### 12. dispatch_once实现原理, 如何保证一段代码只执行一次

```
+ (instancetype )sharedInstance {
    static dispatch_once_t onceToken;
    static SQFlutterLoadChannelManager *_instance;
    dispatch_once(&onceToken, ^{
        if (_instance == nil) {
            _instance = [[SQFlutterLoadChannelManager alloc] init];
        }
    });
    return _instance;
}

// 我们调用dispatch_once的入口
void dispatch_once(dispatch_once_t *val, dispatch_block_t block)
{
    // 内部又调用了dispatch_once_f函数
    dispatch_once_f(val, block, _dispatch_Block_invoke(block));
}

DISPATCH_NOINLINE
void dispatch_once_f(dispatch_once_t *val, void *ctxt, dispatch_function_t func) {
    return dispatch_once_f_slow(val, ctxt, func);
}

DISPATCH_ONCE_SLOW_INLINE
static void
dispatch_once_f_slow(dispatch_once_t *val, void *ctxt, dispatch_function_t func)
{
    // _dispatch_once_waiter_t格式：
    // typedef struct _dispatch_once_waiter_s {
    //      volatile struct _dispatch_once_waiter_s *volatile dow_next;
    //      dispatch_thread_event_s dow_event;
    //      mach_port_t dow_thread;
    // } *_dispatch_once_waiter_t;


    // volatile：告诉编译器不要对此指针进行代码优化，因为这个指针指向的值可能会被其他线程改变
    _dispatch_once_waiter_t volatile *vval = (_dispatch_once_waiter_t*)val;
    struct _dispatch_once_waiter_s dow = { };
    _dispatch_once_waiter_t tail = &dow, next, tmp;
    dispatch_thread_event_t event;

    // 第一次执行时，*vval为0，此时第一个参数vval和第二个参数NULL比较是相等的，返回true，然后把tail赋值给第一个参数的值。如果这时候同时有别的线程也进来，此时vval的值不是0了，所以会来到else分支。
    if (os_atomic_cmpxchg(vval, NULL, tail, acquire)) {
        // 获取当前线程
        dow.dow_thread = _dispatch_tid_self();
        // 调用block函数，一般就是我们在外面做的初始化工作
        _dispatch_client_callout(ctxt, func);

        // 内部将DLOCK_ONCE_DONE赋值给val，将当前标记为已完成，返回之前的引用值。前面说过了，把tail赋值给val了，但这只是没有别的线程进来走到下面else分支，如果有别的线程进来next就是别的值了，如果没有别的信号量在等待，工作就到此结束了。
        next = (_dispatch_once_waiter_t)_dispatch_once_xchg_done(val);
        // 如果没有别的线程进来过处于等待，这里就会结束。如果有，则遍历每一个等待的信号量，然后一个个唤醒它们
        while (next != tail) {
            // 内部用到了thread_switch，避免优先级反转。把next->dow_next返回
            tmp = (_dispatch_once_waiter_t)_dispatch_wait_until(next->dow_next);
            event = &next->dow_event;
            next = tmp;
            // 唤醒信号量
            _dispatch_thread_event_signal(event);
        }
    } else {
        // 内部就是_dispatch_sema4_init函数，也就是初始化一个信号链表
        _dispatch_thread_event_init(&dow.dow_event);
        // next指向新的原子
        next = *vval;
        // 不断循环等待
        for (;;) {
            // 前面说过第一次进来后进入if分支，后面再次进来，会来到这里，但是之前if里面被标志为DISPATCH_ONCE_DONE了，所以结束。
            if (next == DISPATCH_ONCE_DONE) {
                break;
            }
            // 当第一次初始化的时候，同时有别的线程也进来，这是第一个线程已经占据了if分支，但其他线程也是第一进来，所以状态并不是DISPATCH_ONCE_DONE，所以就来到了这里
            // 比较vval和next是否一样，其他线程第一次来这里肯定是相等的
            if (os_atomic_cmpxchgv(vval, next, tail, &next, release)) {
                dow.dow_thread = next->dow_thread;
                dow.dow_next = next;
                if (dow.dow_thread) {
                    pthread_priority_t pp = _dispatch_get_priority();
                    _dispatch_thread_override_start(dow.dow_thread, pp, val);
                }
                // 等待唤醒，唤醒后就做收尾操作
                _dispatch_thread_event_wait(&dow.dow_event);
                if (dow.dow_thread) {

                    _dispatch_thread_override_end(dow.dow_thread, val);
                }
                break;
            }
        }
        // 销毁信号量
        _dispatch_thread_event_destroy(&dow.dow_event);
    }
}
```
<font color=DarkGray>

第一次进，token为空，vval等于NULL，os_atomic_cmpxchg(vval, NULL, tail, acquire)执行完之后vval被赋值tail，再进if就会进else了。

if - _dispatch_client_callout执行block - 将DLOCK_ONCE_DONE赋值给val，将当前标记为已完成 - 唤醒等待线程

else - for (;;)循环 - 判断DISPATCH_ONCE_DONE - 否 - 线程等待
else - for (;;)循环 - 判断DISPATCH_ONCE_DONE - 是 - 跳出循环

https://leylfl.github.io/2018/01/16/%E6%B5%85%E8%B0%88iOS%E5%A4%9A%E7%BA%BF%E7%A8%8B-%E6%BA%90%E7%A0%81/
</font> 

#### 13. 什么是属性，属性与成员变量的区别，如果属性和成员变量同名，如何实现两个不同的
<font color=DarkGray>

“属性” (property)有两大概念：ivar（实例变量）、存取方法（access method ＝ getter + setter）。

完成属性定义后，编译器会自动编写访问这些属性所需的方法，此过程叫做“自动合成”( autosynthesis)。需要强调的是，这个过程由编译 器在编译期执行，所以编辑器里看不到这些“合成方法”(synthesized method)的源代码。除了生成方法代码 getter、setter 之外，编译器还要自动向类中添加适当类型的实例变量，并且在属性名前面加下划线，以此作为实例变量的名字。在前例中，会生成两个实例变量，其名称分别为 _firstName与_lastName。也可以在类的实现代码里通过 @synthesize语法来指定实例变量的名字.

大致生成了五个东西

OBJC_IVAR_$类名$属性名称 ：该属性的“偏移量” (offset)，这个偏移量是“硬编码” (hardcode)，表示该变量距离存放对象的内存区域的起始地址有多远。
setter与getter方法对应的实现函数
ivar_list ：成员变量列表
method_list ：方法列表
prop_list ：属性列表

每次在增加一个属性,系统都会在ivar_list中添加一个成员变量的描述,在method_list中增加setter与getter方法的描述,在属性列表中增加一个属性的描述,然后计算该属性在对象中的偏移量,然后给出setter与getter方法对应的实现,在setter方法中从偏移量的位置开始赋值,在getter方法中从偏移量开始取值,为了能够读取正确字节数,系统对象偏移量的指针类型进行了类型强转

@protocol 和 category 中使用 @property
在protocol中使用property只会生成setter和getter方法声明,我们使用属性的目的,是希望遵守我协议的对象能实现该属性
category 使用 @property 也是只会生成setter和getter方法的声明,如果我们真的需要给category增加属性的实现,需要借助于运行时的关联对象

属性和成员变量同名，如何实现两个不同的
重写setter getter方法

</font> 

#### 14. 事件传递和响应机制，查找的顺序，问到pointInside:withEvent
<font color=DarkGray>
App通过响应者对象来接收和处理事件，响应者对象都是UIResponder的子类对象，常见的UIView，UIVieController、UIWindow和UIApplication都是UIResponder的子类。

事件传递流程
触摸事件的传递是从父控件传递到子控件
</font> 

```
- 当点击屏幕后
- - 事件会传递给UIApplication
- - - - 传递给当前的UIWindow
- - - - - - -UIWindow通过调用- (UIView *)hitTest:(CGPoint)point withEvent:(nullable UIEvent *)event方法返回响应视图。
- - - - - - - - - 其中hitTest:withEvent:内部会调用- (BOOL)pointInside:(CGPoint)point withEvent:(nullable UIEvent *)event方法判断点击位置是否在UIWindow范围内，
- - - - - - - - - - - - 如果是的话就会【倒序遍历】（最后添加的视图最先遍历）UIWindow的子视图，从而找出响应视图并返回。
```

<font color=DarkGray>
hitTest:withEvent:内部都做了什么？

当视图隐藏属性hidden=NO、
交互userInteractionEnabled=YES、
透明度alpha>0.01 三者同时满足才拥有响应能力

若当前视图未拥有响应能力，hitTest方法直接返回nil，并且将当前视图的父视图作为时间响应者返回
若当前视图拥有响应事件能力，则继续判断事件点击位置是否在当前视图范围内，若不在则return nil，若在范围内，则倒序遍历当前视图的子视图，重复以上动作，直到找出响应视图。

事件的响应链机制流程

当事件触发后，系统会自动为我们找到合适的响应对象，响应对象对事件逐级向上响应的过程就是响应链，和事件传递流程可以说是恰好相反

拦截事件的处理

正因为hitTest：withEvent：方法可以返回最合适的view，所以可以通过重写hitTest：withEvent：方法，返回指定的view作为最合适的view。
不管点击哪里，最合适的view都是hitTest：withEvent：方法中返回的那个view。
通过重写hitTest：withEvent：，就可以拦截事件的传递过程，想让谁处理事件谁就处理事件。

所以事件的传递顺序是这样的：
　　产生触摸事件->UIApplication事件队列->[UIWindow hitTest:withEvent:]->返回更合适的view->[子控件 hitTest:withEvent:]->返回最合适的view


如何判断上一个响应者

1> 如果当前这个view是控制器的view,那么控制器就是上一个响应者
2> 如果当前这个view不是控制器的view,那么父控件就是上一个响应者

响应者链的事件传递过程:

1>如果当前view是控制器的view，那么控制器就是上一个响应者，事件就传递给控制器；如果当前view不是控制器的view，那么父视图就是当前view的上一个响应者，事件就传递给它的父视图
2>在视图层次结构的最顶级视图，如果也不能处理收到的事件或消息，则其将事件或消息传递给window对象进行处理
3>如果window对象也不处理，则其将事件或消息传递给UIApplication对象
4>如果UIApplication也不能处理该事件或消息，则将其丢弃

如何做到一个事件多个对象处理：


</font> 

```
- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event { 
    // 1.自己先处理事件...
    NSLog(@"do somthing...");
    // 2.再调用系统的默认做法，再把事件交给上一个响应者处理
    [super touchesBegan:touches withEvent:event]; 
}
```

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

#### 22. KVO的原理
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

