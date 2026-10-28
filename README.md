# mpvvb —— 多极完美矢量涡旋光束（MPVVB）SLM 相位图生成与仿真

本程序包用于生成多极完美矢量涡旋光束的 SLM 相位图，并仿真焦面光强与偏振分布。
矢量涡旋偏振片阶数 **M**、每一层光束的 **d**、**m**、**l**、**β** 以及层权重都可以作为变量设置。

模型由论文 *Dynamic control of multipolar perfect vector vortex beams* 的原始仿真结果（MATLAB `.fig`）反推得到，
在 M = 30 时与原始结果对比：SLM 相位匹配度 0.9915–0.9992，光强图平均相关系数 0.972。

## 目录结构

```
Python_Upload/
├── README.md
├── pyproject.toml          # pip 安装配置
├── requirements.txt
├── mpvvb/
│   ├── __init__.py
│   ├── core.py             # 模型：Layer、slm_phase、simulate
│   ├── fileio.py           # 相位图保存（png/bmp/tif/npy/csv/mat），读取 .fig
│   ├── plotting.py         # 排版的绘图
│   ├── paper.py            # 算例
│   ├── cli.py              # 命令行
│   └── __main__.py
└── examples/
    ├── generate_phase.py              # 改变量即可出相位图的模板
    └── validate_against_reference.py  # 与原始 .fig 结果对比
```

## 安装

需要 Python 3.8 及以上。

```bash
pip install -r requirements.txt     # numpy scipy matplotlib pillow
pip install -e .                    # 可选：安装后任意目录可 import mpvvb，并可用 mpvvb 命令
```

不安装也可以：在 `Python_Upload` 目录下直接运行 `python -m mpvvb ...`，或在脚本中把该目录加入 `sys.path`。

## 快速开始

### 1. Python 调用：生成 SLM 相位图

```python
from mpvvb import Layer, slm_phase, save_phase

phase = slm_phase(
    layers=[Layer(d=0.3, m=0.5), Layer(d=0.5, m=2)],  # 两层：外环 m=0.5，内环 m=2
    M=30,                       # 矢量涡旋偏振片阶数
    shape=(1080, 1920),         # SLM 分辨率 (高, 宽)
    R0=500,                     # 每单位 ρ 对应的 SLM 像素数
)
save_phase(phase, 'slm_phase.png')               # 8 位灰度图，0–255 对应 0–2π
save_phase(phase, 'slm_phase.bmp', gray2pi=213)  # SLM 标定中 2π 对应灰度 213 时
save_phase(phase, 'slm_phase.npy')               # 弧度数据
```

`phase` 是 `shape` 大小的数组，单位为弧度，取值 [0, 2π)。

层也可以直接写成元组 `(d, m)`、`(d, m, l)` 或 `(d, m, l, betaDeg)`：

```python
phase = slm_phase([(0.3, 2.5), (0.45, 2), (1, 1.5)], M=30)   # 三层
```

### 2. 命令行：生成 SLM 相位图

```bash
# 双层，M=30，1000×1000，输出 8 位 PNG
python -m mpvvb phase --M 30 --layer 0.3 0.5 --layer 0.5 2 -o phase.png

# M=20，1920×1080 的 SLM，2π 对应灰度 213，同时输出彩色预览图
python -m mpvvb phase --M 20 --layer 0.4 1.5 --shape 1080 1920 --R0 540 --gray2pi 213 --preview -o slm.bmp

# 自定义权重（外 → 内）、β=45°、指定 l
python -m mpvvb phase --M 30 --layer 0.3 1 0 45 --layer 0.5 2.5 0.5 --weights 1 -0.8 -o phase.png
```

`phase` 子命令的参数：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--M` | 30 | 矢量涡旋偏振片阶数 |
| `--layer d m [l [betaDeg]]` | 必填 | 一层光束，可重复多次 |
| `--weights` | 1 -0.8 0.6 | 层权重（外环 → 内环），可写复数如 `0.5+0.2i` |
| `--shape H W` | 1000 1000 | SLM 像素尺寸（高 宽） |
| `--R0` | 500 | 每单位 ρ 的像素数；锥透镜相位周期 = d × R0 像素 |
| `--center ROW COL` | 图像中心 | 光轴所在像素位置 |
| `--gray2pi` | 255 | 2π 对应的灰度值 |
| `--bits` | 8 | 图像位深，8 或 16 |
| `--preview` | 关 | 额外保存彩色预览图 |
| `-o` | 必填 | 输出文件；`.png/.bmp/.tif` 为灰度图，`.npy/.csv/.mat` 为弧度数据 |

### 3. 仿真焦面光强

```python
from mpvvb import Layer, simulate
from mpvvb.plotting import plot_rows

S = simulate([Layer(0.3, 1.5), Layer(0.5, 3)], M=30)
S['phaseSLM']   # SLM 相位（1000×1000，弧度）
S['Itotal']     # 无检偏器总光强（归一化，500×500）
S['Ia']         # 各检偏角光强，形状 (500, 500, 检偏角个数)
S['Ex'], S['Ey']  # 焦面复振幅
S['quiver']     # 偏振分布箭头数据 X, Y, U, V
plot_rows([S], ['M=30, 1.5/3']).savefig('panel.png')
```

`simulate` 的关键字参数可覆盖 `SimOptions` 中的任意字段，例如
`simulate(layers, M=20, fieldMode='slm', analyzerDeg=[0, 30, 60, 90], hwpDeg=22.5)`。

命令行：

```bash
python -m mpvvb simulate --M 30 --layer 0.3 1.5 --layer 0.5 3 -o out/beam1
# 输出 out/beam1_SLM_phase.png、out/beam1.npz、out/beam1_panel.png
python -m mpvvb simulate --M 30 --layer 0.3 1 --analyzer 0 30 60 90 --hwp 22.5 --mode slm -o out/beam2
```

### 4. 复现论文图2–图5

```bash
python -m mpvvb paper -o paper_outputs
```

### 5. 与原始结果对比

```bash
python examples/validate_against_reference.py            # 默认读取 ../figure
python examples/validate_against_reference.py D:/path/to/figure
```

## 参数含义

### 光束层 `Layer(d, m, l=None, betaDeg=0)`

| 参数 | 含义 |
|---|---|
| `d` | 锥透镜相位的归一化周期。**d 不是直径**：焦面环半径 ∝ 1/d，d 越大环越小。在默认仿真采样下环半径约为 40/d 像素 |
| `m` | 偏振阶数。检偏后每个环出现 2m 个花瓣（0.5 阶为 1 瓣，1.5 阶为 3 瓣） |
| `l` | 标量涡旋拓扑荷。默认：m 为半整数时 l = 0.5，否则 l = 0（对应论文式(2)中 l = 0） |
| `betaDeg` | 偏振方向偏置 β（度） |

多层时，层的书写顺序不影响结果，程序按 d 从小到大（外环 → 内环）排序后分配权重。
默认权重为 `(1, -0.8, 0.6)`，最多覆盖三层；四层及以上需要通过 `weights` 显式给出。

### 仿真参数 `SimOptions`

| 参数 | 默认值 | 含义 |
|---|---|---|
| `M` | 30 | 矢量涡旋偏振片阶数 |
| `R0` | 500 | 仿真光瞳上每单位 ρ 的像素数 |
| `rhoMax` | 2.5 | 圆形光瞳半径（ρ 单位） |
| `w0` | 1.7 | 高斯振幅束腰（ρ 单位），`np.inf` 为平顶 |
| `weights` | None | 层权重，None 时使用默认权重 |
| `fieldMode` | `'ideal'` | `'ideal'`：传播理想复振幅场（与原始仿真最吻合）；`'slm'`：传播纯相位 SLM 场 |
| `nOut` | 500 | 焦面输出窗口尺寸 |
| `df` | 1/19800 | 焦面采样间隔 |
| `circularOutput` | True | 焦面输出取圆形区域 |
| `analyzerDeg` | [0, 45, 90] | 检偏角（度） |
| `hwpDeg` | None | 检偏器前半波片快轴角（度） |
| `phaseCrop` | 1000 | 返回的 SLM 相位窗口尺寸 |
| `quiverN` | 20 | 偏振分布箭头网格数 |

其中 `rhoMax`、`w0`、`df` 和默认权重是对照原始结果拟合得到的，论文中没有给出。
所有坐标均为归一化量；如需换算到实验，需要用 SLM 像素尺寸和透镜焦距标定 `R0`。

## 模型

1. **SLM 相位**：第 k 层的复数项为

   f_k = cos((M − m_k)φ − β_k) · exp(i l_k φ) · exp(−i 2π ρ / d_k)

   SLM 相位 Φ = arg( Σ_k w_k · exp(i·arg f_k) )，ρ = r / R0。
2. **M 阶矢量涡旋偏振片**：x 偏振光变为 E · [cos Mφ, sin Mφ]。
   cos((M − m)φ) 与它拍频得到 m 阶矢量涡旋光束，同时产生一个 (2M − m) 阶分量。
3. **透镜**：用矩阵傅里叶变换计算焦面场，锥透镜相位在焦面形成半径 ∝ 1/d 的完美涡旋环。
4. **检偏**：I = |cos a · Ex + sin a · Ey|²；可选在检偏器前加半波片。

### 关于 M 的选择

(2M − m) 阶分量的能量主要分布在光瞳半径约 ρ ≈ (2M − m)·d / (2π) 处。
当这个值明显大于光瞳的有效半径（默认约 2–2.5）时，该分量被推到环外，只在背景中留下淡条纹；
如果 M 太小或 d 太小，它会漏进环内，使环上出现一串亮点调制。

例如 M = 30、d = 0.3、m = 0.5 时约为 2.8，环很干净；M = 20、d = 0.3、m = 1.5 时约为 1.8，外环会出现明显的点状调制。
改变 M 时，可以先用 `simulate` 检查光强图。

## 验证结果（M = 30）

| 对比项目 | 结果 |
|---|---|
| 12 张 SLM 相位图 | 匹配度 0.9915–0.9992（1 为完全相同） |
| 48 张光强图（总光强及 0°/45°/90°） | 平均相关系数 0.972，最低 0.951 |
| 6 张偏振分布图 | 方向全部一致 |

## 论文算例

| 论文图 | 光束（由外到内） | 代码 |
|---|---|---|
| 图2 整数阶 | m=3 (d=0.2)；m=1 (d=0.3)；m=2 (d=0.5) | `Layer(0.2, 3)` 等 |
| 图3 分数阶 | m=0.5 (d=0.2)；m=1.5 (d=0.3)；m=2.5 (d=0.5) | `Layer(0.2, 0.5)` 等 |
| 图4 双层 | 0.5/2；1.5/3；1/0.5；3/1.5（外环 d=0.3，内环 d=0.5） | `[Layer(0.3, 0.5), Layer(0.5, 2)]` 等 |
| 图5 三层 | 0.5/1/1.5；2.5/2/1.5（d = 0.3/0.45/1） | `[Layer(0.3, 0.5), Layer(0.45, 1), Layer(1, 1.5)]` 等 |

完整列表见 `mpvvb/paper.py`。
