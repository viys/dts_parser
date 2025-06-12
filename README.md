# dts_parser.py 使用说明

## 介绍

`dts_parser.py` 是一个用于解析简化版 Device Tree Source (DTS) 文件的 Python 脚本。
 它支持从 DTS 文件中提取节点和属性信息，自动生成对应的 C 语言宏定义头文件，方便项目中通过宏使用硬件配置。

------

## 支持的 DTS 格式特点

- 以 `/ { ... };` 为根节点结构

- 每个节点格式为：

  ```
  label: type {
      property = value;
      ...
  };
  ```

- 支持三种属性值类型：

  - 字符串：用双引号括起来，如 `"uart0"`
  - 数字（宏定义数值）：用尖括号括起来，如 `<115200>`
  - 宏名或标识符：不带引号和尖括号，如 `GPIO1`

------

## 生成的宏定义格式

- 宏名称格式：`DT_<LABEL>_<PROPERTY>`
- `<LABEL>` 直接转大写，不拆分数字，如 `uart0` 转为 `UART0`
- `<PROPERTY>` 属性名转大写，`-` 替换为 `_`
- 字符串属性值带双引号，数字和宏名原样输出

示例：

```c
/** uart **/
#define DT_UART0_NAME "uart0"
#define DT_UART0_TX_PIN GPIO1
#define DT_UART0_RX_PIN GPIO2
#define DT_UART0_BAUDRATE 115200
```

------

## 使用方法

### 命令格式

```bash
python dts_parser.py <input.dts> <output.h>
```

- `<input.dts>`：待解析的 DTS 文件路径
- `<output.h>`：生成的头文件路径

### 示例

假设你的 DTS 文件是 `dts/myboard.dts`，想生成头文件到 `include/generated.h`，执行：

```bash
python dts_parser.py dts/myboard.dts include/generated.h
```

执行成功后，会在目标路径生成头文件，文件内容类似：

```c
/* Auto-generated devicetree header */

/** uart **/
#define DT_UART0_NAME "uart0"
#define DT_UART0_TX_PIN GPIO1
#define DT_UART0_RX_PIN GPIO2
#define DT_UART0_BAUDRATE 115200
#define DT_UART1_NAME "uart1"
#define DT_UART1_TX_PIN GPIO7
#define DT_UART1_RX_PIN GPIO8
#define DT_UART1_BAUDRATE 921600

/** i2c **/
#define DT_I2C0_SDA_PIN GPIO3
#define DT_I2C0_SCL_PIN GPIO4
#define DT_I2C1_SDA_PIN GPIO5
#define DT_I2C1_SCL_PIN GPIO6

```

------

## 注意事项

- DTS 文件格式必须符合支持的简化格式，节点之间属性必须以分号结尾
- 支持去除 C 风格的 `/* */` 和 `//` 注释
- 不支持复杂的 DTS 语法结构和嵌套
- 生成的宏方便直接在 C 代码中使用，无需手动修改

------

