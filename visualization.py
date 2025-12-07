# =============================================================================
# visualization.py
# 电商用户行为分析与复购预测 - 可视化源文件
# =============================================================================


# =============================================================================
# 1. 环境配置和库导入
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import jinja2
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=DeprecationWarning)
os.environ['LOKY_MAX_CPU_COUNT'] = '1'

# 机器学习相关库
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score, classification_report

# 关联规则
from mlxtend.frequent_patterns import apriori, association_rules

# 可视化设置
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建可视化输出文件文件夹
if not os.path.exists('可视化输出文件'):
    os.makedirs('可视化输出文件')
    print("创建文件夹: 可视化输出文件")

print("可视化脚本环境配置完成")

# =============================================================================
# 2. 数据加载和预处理
# =============================================================================
print("开始加载数据...")

# 优先加载清洗后的文件
if os.path.exists('OnlineRetail_cleaned.csv'):
    print("检测到清洗后的数据文件，直接加载...")
    df_clean = pd.read_csv('OnlineRetail_cleaned.csv')
    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
    print(f"加载清洗后数据: {df_clean.shape} 条记录")
else:
    print("使用原始数据清洗...")
    # 加载数据
    df = pd.read_excel('Online Retail.xlsx')
    print(f"原始数据形状: {df.shape}")

    # 数据清洗
    original_shape = df.shape
    df_clean = df.dropna(subset=['CustomerID'])
    df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
    df_clean = df_clean[~df_clean['InvoiceNo'].astype(str).str.startswith('C')]
    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
    df_clean['TotalAmount'] = df_clean['Quantity'] * df_clean['UnitPrice']

    print(f"清洗完成: 原始数据{original_shape[0]}条 → 清洗后{df_clean.shape[0]}条")

# =============================================================================
# 3. 表格1: 用户特征数据示例表
# =============================================================================
<<<<<<< HEAD
print("开始生成用户特征数据示例表（表1-1）...")
=======
print("开始生成数值变量统计描述表...")

stats_df = df_clean[['Quantity', 'UnitPrice', 'TotalAmount']].describe()

# 保存为HTML格式表格（保持原样式）
html_table = stats_df.style \
    .set_caption('表1-1 数值变量统计描述表') \
    .format({'count': '{:,.0f}', 'mean': '{:.2f}', 'std': '{:.2f}',
             'min': '{:.2f}', '25%': '{:.2f}', '50%': '{:.2f}',
             '75%': '{:.2f}', 'max': '{:.2f}'}) \
    .background_gradient(cmap='Blues') \
    .set_properties(**{'text-align': 'center'}) \
    .to_html()

with open('可视化输出文件/表1-1_数值变量统计描述表.html', 'w', encoding='utf-8') as f:
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
table_data.append(['统计量'] + stats_df.columns.tolist())
for stat_name in stats_df.index:
    row = [stat_name]
    for col in stats_df.columns:
        if stat_name == 'count':
            row.append(f"{stats_df.loc[stat_name, col]:,.0f}")
        else:
            row.append(f"{stats_df.loc[stat_name, col]:.2f}")
    table_data.append(row)

table = ax.table(cellText=table_data,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.15] + [0.28] * len(stats_df.columns))

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(11)

# 设置标题样式
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        if i % 2 == 1:
            table[(i, j)].set_facecolor('#EBF5FB')
        else:
            table[(i, j)].set_facecolor('#F8F9F9')

plt.title('表1-1 数值变量统计描述表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
plt.savefig('可视化输出文件/表1-1_数值变量统计描述表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
stats_df.to_csv('可视化输出文件/表1-1_数值变量统计描述表.csv', encoding='utf-8-sig')
print("表格1保存完成: 可视化输出文件/表1-1_数值变量统计描述表.html/.png/.csv")

# =============================================================================
# 4. 表格2: 用户特征数据示例表
# =============================================================================
print("开始生成用户特征数据示例表...")
>>>>>>> origin/main

# 计算用户特征
snapshot_date = df_clean['InvoiceDate'].max() + timedelta(days=1)

rfm = df_clean.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalAmount': 'sum'
}).reset_index()
rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

df_clean['Hour'] = df_clean['InvoiceDate'].dt.hour
df_clean['TimeSegment'] = pd.cut(df_clean['Hour'],
                                 bins=[0, 6, 12, 18, 24],
                                 labels=['深夜', '上午', '下午', '晚上'],
                                 right=False)

time_pref = df_clean.groupby(['CustomerID', 'TimeSegment']).size().unstack(fill_value=0)
time_pref = time_pref.div(time_pref.sum(axis=1), axis=0)
time_pref = time_pref.reset_index()

user_features = pd.merge(rfm, time_pref, on='CustomerID', how='left').fillna(0)
print(f"用户特征数据形状: {user_features.shape}")

# 选取前5行
sample_data = user_features.head(5).copy()

# 保存为HTML格式表格
html_table = sample_data.style \
    .set_caption('表1-1 用户特征数据示例表') \
    .format({
    'Recency': '{:.0f}天',
    'Frequency': '{:.0f}次',
    'Monetary': '¥{:,.2f}',
    '深夜': '{:.1%}', '上午': '{:.1%}', '下午': '{:.1%}', '晚上': '{:.1%}'
}) \
    .background_gradient(subset=['Recency', 'Frequency', 'Monetary'], cmap='YlGnBu') \
    .background_gradient(subset=['深夜', '上午', '下午', '晚上'], cmap='YlOrRd') \
    .set_properties(**{'text-align': 'center', 'font-size': '11px'}) \
    .to_html()

<<<<<<< HEAD
with open('可视化输出文件/表1-1_用户特征数据示例表.html', 'w', encoding='utf-8') as f:
=======
with open('可视化输出文件/表1-2_用户特征数据示例表.html', 'w', encoding='utf-8') as f:
>>>>>>> origin/main
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(12, 3))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary', '深夜', '上午', '下午', '晚上']
table_data.append(columns)

for idx, row in sample_data.iterrows():
    table_data.append([
        f"{int(row['CustomerID'])}",
        f"{row['Recency']:.0f}天",
        f"{row['Frequency']:.0f}次",
        f"¥{row['Monetary']:,.2f}",
        f"{row['深夜']:.1%}",
        f"{row['上午']:.1%}",
        f"{row['下午']:.1%}",
        f"{row['晚上']:.1%}"
    ])

table = ax.table(cellText=table_data,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.12, 0.1, 0.1, 0.12, 0.08, 0.08, 0.08, 0.08])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(9)

# 设置标题样式
for i in range(len(columns)):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(columns)):
        if i % 2 == 1:
            table[(i, j)].set_facecolor('#F8F9F9')
        else:
            table[(i, j)].set_facecolor('#EBF5FB')

plt.title('表1-1 用户特征数据示例表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
<<<<<<< HEAD
plt.savefig('可视化输出文件/表1-1_用户特征数据示例表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
sample_data.to_csv('可视化输出文件/表1-1_用户特征数据示例表.csv', encoding='utf-8-sig', index=False)
print("表格1保存完成: 可视化输出文件/表1-1_用户特征数据示例表.html/.png/.csv")
=======
plt.savefig('可视化输出文件/表1-2_用户特征数据示例表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
sample_data.to_csv('可视化输出文件/表1-2_用户特征数据示例表.csv', encoding='utf-8-sig', index=False)
print("表格2保存完成: 可视化输出文件/表1-2_用户特征数据示例表.html/.png/.csv")
>>>>>>> origin/main

# =============================================================================
# 4. 表格2: 商品特征数据示例表
# =============================================================================
print("开始生成商品特征数据示例表（表1-2）...")

product_features = df_clean.groupby('StockCode').agg({
    'InvoiceNo': 'nunique',
    'Quantity': ['mean', 'sum'],
    'CustomerID': 'nunique'
}).round(2)
product_features.columns = ['购买频次', '平均订单量', '总销量', '购买用户数']

# 选取前5行
product_sample = product_features.head(5).reset_index()

# 保存为HTML格式表格
html_table = product_sample.style \
    .set_caption('表1-2 商品特征数据示例表') \
    .format({
    '购买频次': '{:.0f}次',
    '平均订单量': '{:.2f}件',
    '总销量': '{:,.0f}件',
    '购买用户数': '{:.0f}人'
}) \
    .background_gradient(subset=['购买频次', '总销量', '购买用户数'], cmap='YlGnBu') \
    .background_gradient(subset=['平均订单量'], cmap='YlOrRd') \
    .set_properties(**{'text-align': 'center', 'font-size': '11px'}) \
    .to_html()

<<<<<<< HEAD
with open('可视化输出文件/表1-2_商品特征数据示例表.html', 'w', encoding='utf-8') as f:
=======
with open('可视化输出文件/表1-3_商品特征数据示例表.html', 'w', encoding='utf-8') as f:
>>>>>>> origin/main
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(10, 3))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
columns = ['StockCode', '购买频次', '平均订单量', '总销量', '购买用户数']
table_data.append(columns)

for idx, row in product_sample.iterrows():
    table_data.append([
        f"{row['StockCode']}",
        f"{row['购买频次']:.0f}次",
        f"{row['平均订单量']:.2f}件",
        f"{row['总销量']:,.0f}件",
        f"{row['购买用户数']:.0f}人"
    ])

table = ax.table(cellText=table_data,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.15, 0.15, 0.15, 0.15, 0.15])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(9)

# 设置标题样式
for i in range(len(columns)):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(columns)):
        if i % 2 == 1:
            table[(i, j)].set_facecolor('#F8F9F9')
        else:
            table[(i, j)].set_facecolor('#EBF5FB')

plt.title('表1-2 商品特征数据示例表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
<<<<<<< HEAD
plt.savefig('可视化输出文件/表1-2_商品特征数据示例表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
product_sample.to_csv('可视化输出文件/表1-2_商品特征数据示例表.csv', encoding='utf-8-sig', index=False)
print("表格2保存完成: 可视化输出文件/表1-2_商品特征数据示例表.html/.png/.csv")

# =============================================================================
# 5. 表格3: 预处理后数据集概览表
# =============================================================================
print("开始生成预处理后数据集概览表（表1-3）...")

# 计算数据集概览统计
overview_data = [
    ['数据集总行数', f"{df_clean.shape[0]:,} 行"],
    ['数据集总列数', f"{df_clean.shape[1]} 列"],
    ['缺失值总数', f"{df_clean.isnull().sum().sum():,} 个"],
    ['缺失值比例', f"{(df_clean.isnull().sum().sum() / (df_clean.shape[0] * df_clean.shape[1]) * 100):.4f}%"],
    ['', ''],
    ['唯一客户数量', f"{df_clean['CustomerID'].nunique():,} 个"],
    ['唯一商品数量', f"{df_clean['StockCode'].nunique():,} 个"],
    ['唯一订单数量', f"{df_clean['InvoiceNo'].nunique():,} 个"],
    ['', ''],
    ['总交易数量', f"{df_clean['Quantity'].sum():,} 件"],
    ['总交易金额', f"¥{df_clean['TotalAmount'].sum():,.2f}"],
    ['平均订单金额', f"¥{df_clean['TotalAmount'].mean():,.2f}"],
    ['最大订单金额', f"¥{df_clean['TotalAmount'].max():,.2f}"],
    ['最小订单金额', f"¥{df_clean['TotalAmount'].min():,.2f}"],
    ['', ''],
    ['最早订单日期', df_clean['InvoiceDate'].min().strftime('%Y-%m-%d')],
    ['最晚订单日期', df_clean['InvoiceDate'].max().strftime('%Y-%m-%d')],
    ['订单时间跨度', f"{(df_clean['InvoiceDate'].max() - df_clean['InvoiceDate'].min()).days} 天"],
    ['', ''],
    ['数值型变量数量', f"{len(df_clean.select_dtypes(include=['int64', 'float64']).columns)} 个"],
    ['类别型变量数量', f"{len(df_clean.select_dtypes(include=['object']).columns)} 个"],
    ['日期型变量数量', f"{len(df_clean.select_dtypes(include=['datetime64']).columns)} 个"],
    ['', ''],
    ['平均订单数量', f"{df_clean['Quantity'].mean():.2f} 件/单"],
    ['平均商品单价', f"¥{df_clean['UnitPrice'].mean():.2f}"]
]

# 创建DataFrame
overview_df = pd.DataFrame(overview_data, columns=['指标', '数值'])

# 保存为HTML格式表格
html_table = overview_df.style \
    .set_caption('表1-3 预处理后数据集概览表') \
    .hide(axis="index") \
    .set_table_styles([
        {'selector': 'caption', 'props': [('font-size', '16px'),
                                         ('font-weight', 'bold'),
                                         ('color', '#2E4057')]},
        {'selector': 'th', 'props': [('background-color', '#3498DB'),
                                     ('color', 'white'),
                                     ('font-weight', 'bold')]},
        {'selector': 'td', 'props': [('border', '1px solid #BDC3C7'),
                                     ('padding', '8px')]},
        {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#F8F9F9')]},
        {'selector': 'tr:nth-child(odd)', 'props': [('background-color', '#EBF5FB')]}
    ]) \
    .apply(lambda x: ['color: #E74C3C' if '缺失' in x['指标'] else '' for _ in x], axis=1, subset=['指标']) \
    .to_html()

with open('可视化输出文件/表1-3_预处理后数据集概览表.html', 'w', encoding='utf-8') as f:
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
table_data.append(['指标', '数值'])
for item in overview_data:
    table_data.append([item[0], item[1]])

table = ax.table(cellText=table_data,
                 cellLoc='left',
                 loc='center',
                 colWidths=[0.5, 0.5])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(10)

# 设置标题样式
for i in range(2):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(2):
        if table_data[i][0] == '':  # 空行
            table[(i, j)].set_facecolor('#F2F4F4')
            table[(i, j)].set_edgecolor('#F2F4F4')
        else:
            if '缺失' in table_data[i][0]:
                table[(i, j)].set_facecolor('#FDEDEC')
            elif '总行数' in table_data[i][0] or '总交易金额' in table_data[i][0] or '唯一客户' in table_data[i][0]:
                table[(i, j)].set_facecolor('#D5F4E6')
            else:
                table[(i, j)].set_facecolor('#F8F9F9' if i % 2 == 1 else '#EBF5FB')

plt.title('表1-3 预处理后数据集概览表', fontsize=16, pad=20, fontweight='bold')
plt.tight_layout()
plt.savefig('可视化输出文件/表1-3_预处理后数据集概览表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
overview_df.to_csv('可视化输出文件/表1-3_预处理后数据集概览表.csv', encoding='utf-8-sig', index=False)
print("表格3保存完成: 可视化输出文件/表1-3_预处理后数据集概览表.html/.png/.csv")
=======
plt.savefig('可视化输出文件/表1-3_商品特征数据示例表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
product_sample.to_csv('可视化输出文件/表1-3_商品特征数据示例表.csv', encoding='utf-8-sig', index=False)
print("表格3保存完成: 可视化输出文件/表1-3_商品特征数据示例表.html/.png/.csv")
>>>>>>> origin/main

# =============================================================================
# 6. 表格4: 前5条关联规则表
# =============================================================================
print("开始生成关联规则表（表2-1）...")

# 准备交易篮数据
basket = df_clean.groupby(['InvoiceNo', 'StockCode'])['Quantity'].sum().unstack().fillna(0)
basket_binary = (basket > 0).astype(bool)

# 关联规则挖掘
frequent_itemsets = apriori(basket_binary, min_support=0.01, use_colnames=True, max_len=2, low_memory=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
rules = rules.sort_values('lift', ascending=False)

# 选取前5条
top_rules = rules.head(5)[['antecedents', 'consequents', 'support', 'confidence', 'lift']].copy()
top_rules['antecedents'] = top_rules['antecedents'].apply(lambda x: str(set(x)).replace('{', '').replace('}', ''))
top_rules['consequents'] = top_rules['consequents'].apply(lambda x: str(set(x)).replace('{', '').replace('}', ''))

# 保存为HTML格式表格
html_table = top_rules.style \
    .set_caption('表2-1 前5条关联规则表') \
    .format({
    'support': '{:.4f}',
    'confidence': '{:.4f}',
    'lift': '{:.2f}'
}) \
    .background_gradient(subset=['support', 'confidence', 'lift'], cmap='Blues') \
    .set_properties(**{'text-align': 'center'}) \
    .to_html()

<<<<<<< HEAD
with open('可视化输出文件/表2-1_前5条关联规则表.html', 'w', encoding='utf-8') as f:
=======
with open('可视化输出文件/表1-3_前5条关联规则表.html', 'w', encoding='utf-8') as f:
>>>>>>> origin/main
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(12, 3))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
columns = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
table_data.append(['前件', '后件', '支持度', '置信度', '提升度'])

for idx, row in top_rules.iterrows():
    table_data.append([
        row['antecedents'][:30] + '...' if len(row['antecedents']) > 30 else row['antecedents'],
        row['consequents'][:30] + '...' if len(row['consequents']) > 30 else row['consequents'],
        f"{row['support']:.4f}",
        f"{row['confidence']:.4f}",
        f"{row['lift']:.2f}"
    ])

table = ax.table(cellText=table_data,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.25, 0.25, 0.1, 0.1, 0.1])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(9)

# 设置标题样式
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        if i % 2 == 1:
            table[(i, j)].set_facecolor('#F8F9F9')
        else:
            table[(i, j)].set_facecolor('#EBF5FB')

plt.title('表2-1 前5条关联规则表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
<<<<<<< HEAD
plt.savefig('可视化输出文件/表2-1_前5条关联规则表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
top_rules.to_csv('可视化输出文件/表2-1_前5条关联规则表.csv', encoding='utf-8-sig', index=False)
print("表格4保存完成: 可视化输出文件/表2-1_前5条关联规则表.html/.png/.csv")
=======
plt.savefig('可视化输出文件/表1-3_前5条关联规则表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
top_rules.to_csv('可视化输出文件/表1-3_前5条关联规则表.csv', encoding='utf-8-sig', index=False)
print("表格4保存完成: 可视化输出文件/表1-3_前5条关联规则表.html/.png/.csv")
>>>>>>> origin/main

# =============================================================================
# 7. 图表1: 用户分群三维散点图
# =============================================================================
print("开始绘制用户分群三维散点图...")

# 数据标准化
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(user_features[['Recency', 'Frequency', 'Monetary']])

# K-Means聚类
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
user_features['Cluster'] = kmeans.fit_predict(rfm_scaled)

# 定义用户标签
cluster_labels = {0: '高价值活跃用户', 1: '潜力价值用户',
                  2: '一般价值用户', 3: '流失风险用户'}
user_features['Cluster_Label'] = user_features['Cluster'].map(cluster_labels)

# 三维散点图
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

colors = ['red', 'blue', 'green', 'orange']
for i in range(4):
    cluster_data = user_features[user_features['Cluster'] == i]
    ax.scatter(cluster_data['Recency'], cluster_data['Frequency'],
               cluster_data['Monetary'], c=colors[i],
               label=cluster_labels[i], alpha=0.6)

ax.set_xlabel('Recency (天)')
ax.set_ylabel('Frequency (次)')
ax.set_zlabel('Monetary (元)')
ax.legend()
plt.title('图2-1 用户分群三维散点图')
plt.savefig('可视化输出文件/图2-1_用户分群三维散点图.png', dpi=300, bbox_inches='tight')
plt.show()
print("图表1保存完成: 可视化输出文件/图2-1_用户分群三维散点图.png")

# =============================================================================
# 8. 表格5: 用户群体定义表（表2-2，保持不变）
# =============================================================================
print("开始生成用户群体定义表（表2-2）...")

# 计算各群体统计
cluster_stats = user_features.groupby('Cluster_Label').agg({
    'CustomerID': 'count',
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean'
}).reset_index()

cluster_stats['占比'] = (cluster_stats['CustomerID'] / cluster_stats['CustomerID'].sum() * 100).round(1)

# 添加特征描述
feature_descriptions = {
    '高价值活跃用户': '近期活跃、高频高价值',
    '潜力价值用户': '中等活跃、有提升空间',
    '一般价值用户': '低频次、一般价值',
    '流失风险用户': '长期未购、流失风险高'
}
cluster_stats['特征描述'] = cluster_stats['Cluster_Label'].map(feature_descriptions)

# 重命名列
cluster_stats.columns = ['用户类型', '用户数量', 'Recency均值', 'Frequency均值', 'Monetary均值', '占比', '特征描述']

# 保存为HTML格式表格
html_table = cluster_stats.style \
    .set_caption('表2-2 用户群体定义表') \
    .format({
    '用户数量': '{:,}',
    '占比': '{:.1f}%',
    'Recency均值': '{:.1f}天',
    'Frequency均值': '{:.1f}次',
    'Monetary均值': '¥{:,.0f}'
}) \
    .background_gradient(cmap='Blues') \
    .set_properties(**{'text-align': 'center'}) \
    .to_html()

with open('可视化输出文件/表2-2_用户群体定义表.html', 'w', encoding='utf-8') as f:
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(12, 5))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
table_data.append(['用户类型', '用户数量', 'Recency均值', 'Frequency均值', 'Monetary均值', '占比', '特征描述'])

for idx, row in cluster_stats.iterrows():
    table_data.append([
        row['用户类型'],
        f"{row['用户数量']:,}",
        f"{row['Recency均值']:.1f}天",
        f"{row['Frequency均值']:.1f}次",
        f"¥{row['Monetary均值']:,.0f}",
        f"{row['占比']:.1f}%",
        row['特征描述']
    ])

table = ax.table(cellText=table_data,
                 cellLoc='center',
                 loc='center',
                 colWidths=[0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.25])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(9)

# 设置标题样式
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        if i % 2 == 1:
            table[(i, j)].set_facecolor('#F8F9F9')
        else:
            table[(i, j)].set_facecolor('#EBF5FB')

plt.title('表2-2 用户群体定义表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
plt.savefig('可视化输出文件/表2-2_用户群体定义表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
cluster_stats.to_csv('可视化输出文件/表2-2_用户群体定义表.csv', encoding='utf-8-sig', index=False)
print("表格5保存完成: 可视化输出文件/表2-2_用户群体定义表.html/.png/.csv")

# =============================================================================
# 9. 图表2: 特征重要性排名图
# =============================================================================
print("开始绘制特征重要性排名图...")

# 准备复购预测数据
analysis_date = df_clean['InvoiceDate'].max()
cutoff_date = analysis_date - timedelta(days=30)

historical_data = df_clean[df_clean['InvoiceDate'] <= cutoff_date]
rfm_historical = historical_data.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (cutoff_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalAmount': 'sum'
}).reset_index()
rfm_historical.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

future_data = df_clean[df_clean['InvoiceDate'] > cutoff_date]
repurchase_users = future_data['CustomerID'].unique()
last_purchase = df_clean.groupby('CustomerID')['InvoiceDate'].max().reset_index()
last_purchase['Repurchase'] = last_purchase['CustomerID'].isin(repurchase_users).astype(int)

model_data = pd.merge(rfm_historical, last_purchase[['CustomerID', 'Repurchase']],
                      on='CustomerID', how='inner')

feature_cols = ['Recency', 'Frequency', 'Monetary']
X = model_data[feature_cols]
y = model_data['Repurchase']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3,
                                                    random_state=42, stratify=y)

# 三种算法对比
models = {
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'DecisionTree': DecisionTreeClassifier(random_state=42),
    'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000)
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    print(f"{name} F1分数: {f1:.4f}")

# 选择最佳模型
best_model_name = max(models.keys(), key=lambda x: f1_score(y_test, models[x].predict(X_test)))
best_model = models[best_model_name]
print(f"最佳模型: {best_model_name}")

# 特征重要性图
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(importances)), importances[indices],
                   color=plt.cm.YlGnBu(np.linspace(0.4, 0.8, len(importances))))
    plt.xlabel('特征名称', fontsize=12)
    plt.ylabel('Gini重要性', fontsize=12)
    plt.title('图3-1 特征重要性排名图', fontsize=14, pad=20)
    plt.xticks(range(len(importances)), [feature_cols[i] for i in indices], rotation=45)

    # 添加数值标签
    for i, (bar, imp) in enumerate(zip(bars, importances[indices])):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                 f'{imp:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('可视化输出文件/图3-1_特征重要性排名图.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("图表2保存完成: 可视化输出文件/图3-1_特征重要性排名图.png")

# =============================================================================
# 10. 图表3: 混淆矩阵图
# =============================================================================
print("开始绘制混淆矩阵图...")

y_pred = best_model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['不复购', '复购'],
            yticklabels=['不复购', '复购'])
plt.xlabel('预测标签', fontsize=12)
plt.ylabel('实际标签', fontsize=12)
plt.title('图3-2 混淆矩阵图', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('可视化输出文件/图3-2_混淆矩阵图.png', dpi=300, bbox_inches='tight')
plt.show()
print("图表3保存完成: 可视化输出文件/图3-2_混淆矩阵图.png")

# =============================================================================
# 11. 表格6: 分群营销策略表（表5-1，保持不变）
# =============================================================================
print("开始生成分群营销策略表（表5-1）...")

# 定义各用户群体的营销策略
strategies = {
    '高价值活跃用户': [
        'VIP专属优惠和提前访问权',
        '个性化产品推荐和专属客服',
        '忠诚度计划升级和积分加倍奖励'
    ],
    '潜力价值用户': [
        '跨品类购买激励和优惠券',
        '会员升级特惠和专属权益',
        '社交分享奖励和邀请机制'
    ],
    '一般价值用户': [
        '常规促销活动精准推送',
        '新品上市优先体验机会',
        '购物车提醒和满减优惠'
    ],
    '流失风险用户': [
        '定向召回优惠券和限时特惠',
        '个性化关怀邮件和短信提醒',
        '流失预警和专属客户经理服务'
    ]
}

# 生成营销策略表
strategy_table = []
for cluster, strategy_list in strategies.items():
    for i, strategy in enumerate(strategy_list):
        strategy_table.append({
            '用户类型': cluster if i == 0 else '',  # 只在第一行显示用户类型
            '推荐营销动作': strategy
        })

strategy_df = pd.DataFrame(strategy_table)

# 保存为HTML格式表格
html_table = strategy_df.style \
    .set_caption('表5-1 分群营销策略表') \
    .set_properties(**{
    'text-align': 'left',
    'font-size': '12px',
    'font-family': 'Arial, sans-serif'
}) \
    .set_table_styles([
    {'selector': 'caption', 'props': [
        ('font-size', '16px'),
        ('font-weight', 'bold'),
        ('color', '#2E4057')
    ]},
    {'selector': 'th', 'props': [
        ('background-color', '#3498DB'),
        ('color', 'white'),
        ('font-weight', 'bold'),
        ('border', '1px solid #2980B9')
    ]},
    {'selector': 'td', 'props': [
        ('border', '1px solid #BDC3C7')
    ]},
    {'selector': 'tr:nth-child(4n+1)', 'props': [('background-color', '#F8F9F9')]},
    {'selector': 'tr:nth-child(4n+2)', 'props': [('background-color', '#EBF5FB')]},
    {'selector': 'tr:nth-child(4n+3)', 'props': [('background-color', '#F8F9F9')]},
    {'selector': 'tr:nth-child(4n+4)', 'props': [('background-color', '#EBF5FB')]}
]) \
    .to_html()

with open('可视化输出文件/表5-1_分群营销策略表.html', 'w', encoding='utf-8') as f:
    f.write(html_table)

# 同时保存为图片格式
fig, ax = plt.subplots(figsize=(10, 8))
ax.axis('tight')
ax.axis('off')

# 创建表格
table_data = []
table_data.append(['用户类型', '推荐营销动作'])

for idx, row in strategy_df.iterrows():
    table_data.append([
        row['用户类型'],
        row['推荐营销动作']
    ])

table = ax.table(cellText=table_data,
                 cellLoc='left',
                 loc='center',
                 colWidths=[0.2, 0.7])

# 设置字体
table.auto_set_font_size(False)
table.set_fontsize(10)

# 设置标题样式
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#3498DB')
    table[(0, i)].set_text_props(weight='bold', color='white')

# 设置数据行样式
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        if (i - 1) // 3 == 0:  # 高价值活跃用户
            if i % 2 == 1:
                table[(i, j)].set_facecolor('#F8F9F9')
            else:
                table[(i, j)].set_facecolor('#EBF5FB')
        elif (i - 1) // 3 == 1:  # 潜力价值用户
            if i % 2 == 1:
                table[(i, j)].set_facecolor('#E8F8F5')
            else:
                table[(i, j)].set_facecolor('#D1F2EB')
        elif (i - 1) // 3 == 2:  # 一般价值用户
            if i % 2 == 1:
                table[(i, j)].set_facecolor('#FEF9E7')
            else:
                table[(i, j)].set_facecolor('#FCF3CF')
        else:  # 流失风险用户
            if i % 2 == 1:
                table[(i, j)].set_facecolor('#FDEDEC')
            else:
                table[(i, j)].set_facecolor('#FBEEE6')

plt.title('表5-1 分群营销策略表', fontsize=14, pad=20, fontweight='bold')
plt.tight_layout()
plt.savefig('可视化输出文件/表5-1_分群营销策略表.png', dpi=300, bbox_inches='tight')
plt.show()

# 保存为CSV
strategy_df.to_csv('可视化输出文件/表5-1_分群营销策略表.csv', encoding='utf-8-sig', index=False)
print("表格6保存完成: 可视化输出文件/表5-1_分群营销策略表.html/.png/.csv")

# =============================================================================
# 12. 输出总结
# =============================================================================
print("\n" + "=" * 60)
print("所有图表和表格生成完成!")
print("=" * 60)
print("\n生成的文件列表 (保存在'可视化输出文件'文件夹中):")
print("表格文件 (HTML/PNG/CSV格式):")
print("1. 表1-1_用户特征数据示例表")
print("2. 表1-2_商品特征数据示例表")
print("3. 表1-3_预处理后数据集概览表")
print("4. 表2-1_前5条关联规则表")
print("5. 表2-2_用户群体定义表")
print("6. 表5-1_分群营销策略表")
print("\n图表文件 (PNG格式):")
print("1. 图2-1_用户分群三维散点图.png")
print("2. 图3-1_特征重要性排名图.png")
print("3. 图3-2_混淆矩阵图.png")
print(f"\n总计生成 9 个文件 (6个表格 + 3个图表) 到 '可视化输出文件' 文件夹!")