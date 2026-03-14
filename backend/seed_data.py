"""
生成测试数据脚本
运行此脚本可以生成一些示例数据用于测试
"""
from database import SessionLocal
import models
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    
    try:
        # 清空现有数据（可选）
        # db.query(models.Bug).delete()
        # db.query(models.TestProgress).delete()
        # db.query(models.KPIMetric).delete()
        
        # 创建测试进度数据
        fr_descriptions = [
            '用户登录认证FR', '数据导出FR', '报表生成FR', '权限管理FR', '消息推送FR',
            '文件上传FR', '搜索筛选FR', '批量操作FR', '定时任务FR', '日志审计FR'
        ]
        config_methods = [
            '通过 config.yaml 配置相关参数',
            '在管理后台-系统设置中配置',
            '环境变量 CONFIG_XXX 控制',
            '数据库配置表 sys_config',
        ]
        test_names = ['回归测试', '性能测试', '压力测试', '功能测试', '集成测试']
        
        test_progresses = []
        for i in range(10):
            # 随机分配 L0/L2/L4 用例数
            l0_t = random.randint(10, 150)
            l0_p = random.randint(0, l0_t)
            l2_t = random.randint(10, 200)
            l2_p = random.randint(0, l2_t)
            l4_t = random.randint(10, 150)
            l4_p = random.randint(0, l4_t)
            total = l0_t + l2_t + l4_t
            passed = l0_p + l2_p + l4_p
            failed = (l0_t - l0_p) + (l2_t - l2_p) + (l4_t - l4_p)
            progress = round(passed / total * 100, 2) if total > 0 else 0
            fr = random.choice(fr_descriptions)
            test_progress = models.TestProgress(
                test_name=f"{random.choice(test_names)}-{i+1}",
                model_name=fr,
                description=f"该功能实现{fr}相关能力，包括输入校验、业务逻辑处理、异常处理等。支持多场景覆盖。",
                config_method=random.choice(config_methods),
                status=random.choice(['pending', 'running', 'completed', 'failed']),
                progress=progress,
                l0_total_cases=l0_t,
                l0_passed_cases=l0_p,
                l2_total_cases=l2_t,
                l2_passed_cases=l2_p,
                l4_total_cases=l4_t,
                l4_passed_cases=l4_p,
                total_cases=total,
                passed_cases=passed,
                failed_cases=failed,
                test_owners=",".join(random.sample(["张三", "李四", "王五", "赵六"], random.randint(1, 2))),
                developers=",".join(random.sample(["开发A", "开发B", "开发C"], random.randint(1, 2)))
            )
            test_progresses.append(test_progress)
            db.add(test_progress)
        
        db.commit()
        
        # 创建Bug数据
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        bug_titles = [
            '内存泄漏问题', '性能下降', 'UI显示异常', '数据不一致',
            '接口超时', '并发问题', '缓存失效', '日志错误'
        ]
        
        for i in range(20):
            bug = models.Bug(
                test_progress_id=random.choice([tp.id for tp in test_progresses]),
                title=f"{random.choice(bug_titles)}-{i+1}",
                description=f"这是Bug #{i+1}的详细描述",
                severity=random.choice(severities),
                status=random.choice(statuses),
                assigned_to=f"Developer-{random.randint(1, 5)}"
            )
            db.add(bug)
        
        db.commit()
        
        # 创建KPI指标数据
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'latency']
        
        for model_name in models_list:
            for metric_name in metrics:
                # 为每个模型创建多个时间点的数据
                for days_ago in range(30):
                    test_date = datetime.now() - timedelta(days=days_ago)
                    if metric_name == 'latency':
                        # 延迟值（毫秒）
                        value = random.uniform(10, 500)
                    else:
                        # 其他指标（0-1之间的值）
                        value = random.uniform(0.7, 0.99)
                    
                    kpi_metric = models.KPIMetric(
                        model_name=model_name,
                        metric_name=metric_name,
                        metric_value=value,
                        test_date=test_date
                    )
                    db.add(kpi_metric)
        
        db.commit()
        print("测试数据生成成功！")
        print(f"- 测试进度: {len(test_progresses)} 条")
        print(f"- Bug记录: 20 条")
        print(f"- KPI指标: {len(models_list) * len(metrics) * 30} 条")
        
    except Exception as e:
        db.rollback()
        print(f"生成数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # 先初始化数据库
    from backend.init_db import init_db
    init_db()
    
    # 生成测试数据
    seed_data()
