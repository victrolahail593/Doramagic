import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti TC', 'sans-serif']
import seaborn as sns
import numpy as np

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('WHY 提取实验热力图', fontsize=16, fontweight='bold', y=1.02)

# ========================================
# 热力图 1: 版本演进 (项目×模型 vs 版本)
# ========================================
data1 = np.array([
    [7.0, 7.3, 7.86],   # Sonnet-vnpy
    [7.1, 7.6, 7.88],   # Sonnet-daily
    [5.3, 6.6, 7.63],   # Sonnet-funNLP
    [6.5, 6.3, 7.14],   # Gemini-vnpy
    [5.8, 6.4, 7.17],   # Gemini-daily
    [4.2, 5.0, 5.58],   # Gemini-funNLP
])
rows1 = ['S-vnpy', 'S-daily', 'S-funNLP', 'G-vnpy', 'G-daily', 'G-funNLP']
cols1 = ['v1\n(baseline)', 'v2\n(+prompt)', 'v3\n(+stage0)']

ax1 = axes[0]
sns.heatmap(data1, annot=True, fmt='.1f', cmap='RdYlGn', vmin=4, vmax=8.5,
            xticklabels=cols1, yticklabels=rows1, ax=ax1,
            linewidths=0.5, linecolor='white',
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax1.set_title('版本演进', fontsize=13, fontweight='bold', pad=10)

# ========================================
# 热力图 2: v3 维度诊断 (每个WHY的4维度得分)
# ========================================
# Sonnet v3 各项目平均维度得分
data2 = np.array([
    [2.0, 2.0, 1.71, 2.0],   # S-vnpy (证据全满, 因果全满, 增量有1个7分, 工具全满)
    [2.0, 2.0, 1.88, 2.0],   # S-daily
    [2.0, 2.0, 2.0, 1.63],   # S-funNLP (工具价值偏低)
    [1.86, 1.86, 1.29, 2.0],  # G-vnpy
    [1.83, 2.0, 1.50, 2.0],   # G-daily
    [1.33, 1.83, 1.50, 0.83], # G-funNLP
])
rows2 = ['S-vnpy', 'S-daily', 'S-funNLP', 'G-vnpy', 'G-daily', 'G-funNLP']
cols2 = ['证据\n锚定', '因果\n完整', '信息\n增量', '工具\n价值']

ax2 = axes[1]
sns.heatmap(data2, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0.5, vmax=2.0,
            xticklabels=cols2, yticklabels=rows2, ax=ax2,
            linewidths=0.5, linecolor='white',
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title('v3 维度诊断', fontsize=13, fontweight='bold', pad=10)

# ========================================
# 热力图 3: 改进幅度 (v1→v2 vs v2→v3)
# ========================================
data3 = np.array([
    [0.3, 0.56],    # vnpy: Sonnet
    [0.5, 0.28],    # daily: Sonnet
    [1.3, 1.03],    # funNLP: Sonnet
    [-0.2, 0.84],   # vnpy: Gemini
    [0.6, 0.77],    # daily: Gemini
    [0.8, 0.58],    # funNLP: Gemini
])
rows3 = ['S-vnpy', 'S-daily', 'S-funNLP', 'G-vnpy', 'G-daily', 'G-funNLP']
cols3 = ['v1→v2\n(Prompt改进)', 'v2→v3\n(Stage0改进)']

ax3 = axes[2]
sns.heatmap(data3, annot=True, fmt='+.2f', cmap='RdYlGn', vmin=-0.5, vmax=1.5,
            xticklabels=cols3, yticklabels=rows3, ax=ax3,
            linewidths=0.5, linecolor='white',
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax3.set_title('改进幅度 (delta)', fontsize=13, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig('/Users/tang/Documents/vibecoding/Doramagic/experiments/exp-why-extraction/heatmap_why_experiment.png',
            dpi=150, bbox_inches='tight', facecolor='white')
print('saved')
