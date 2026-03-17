"""
Seed data generation script.
Run this script to populate the database with example data for testing.
"""
from database import SessionLocal
import models
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    
    try:
        # Clear existing data if needed.
        # db.query(models.Bug).delete()
        # db.query(models.TestProgress).delete()
        # db.query(models.KPIMetric).delete()
        
        # Create test progress records.
        fr_descriptions = [
            'User Login Authentication FR', 'Data Export FR', 'Report Generation FR', 'Permission Management FR', 'Message Notification FR',
            'File Upload FR', 'Search and Filter FR', 'Batch Operation FR', 'Scheduled Task FR', 'Log Auditing FR'
        ]
        config_methods = [
            'Configure related parameters through config.yaml',
            'Configure through Admin Console > System Settings',
            'Controlled by CONFIG_XXX environment variables',
            'Stored in the sys_config database table',
        ]
        test_names = ['Regression Test', 'Performance Test', 'Stress Test', 'Functional Test', 'Integration Test']
        
        test_progresses = []
        for i in range(10):
            # Randomly assign L0/L2/L4 case counts.
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
                description=f"This feature implements capabilities related to {fr}, including input validation, business logic handling, exception handling, and multi-scenario coverage.",
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
                test_owners=",".join(random.sample(["Alice", "Bob", "Charlie", "Diana"], random.randint(1, 2))),
                developers=",".join(random.sample(["Developer-A", "Developer-B", "Developer-C"], random.randint(1, 2)))
            )
            test_progresses.append(test_progress)
            db.add(test_progress)
        
        db.commit()
        
        # Create bug records.
        severities = ['critical', 'high', 'medium', 'low']
        statuses = ['open', 'in_progress', 'resolved', 'closed']
        bug_titles = [
            'Memory Leak', 'Performance Degradation', 'UI Rendering Issue', 'Data Inconsistency',
            'API Timeout', 'Concurrency Issue', 'Cache Failure', 'Logging Error'
        ]
        
        for i in range(20):
            bug = models.Bug(
                test_progress_id=random.choice([tp.id for tp in test_progresses]),
                title=f"{random.choice(bug_titles)}-{i+1}",
                description=f"Detailed description for bug #{i+1}",
                severity=random.choice(severities),
                status=random.choice(statuses),
                assigned_to=f"Developer-{random.randint(1, 5)}"
            )
            db.add(bug)
        
        db.commit()
        
        # Create KPI metric records.
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'latency']
        
        for model_name in models_list:
            for metric_name in metrics:
                # Create data points for multiple dates for each model.
                for days_ago in range(30):
                    test_date = datetime.now() - timedelta(days=days_ago)
                    if metric_name == 'latency':
                        # Latency value in milliseconds.
                        value = random.uniform(10, 500)
                    else:
                        # Other metrics are values between 0 and 1.
                        value = random.uniform(0.7, 0.99)
                    
                    kpi_metric = models.KPIMetric(
                        model_name=model_name,
                        metric_name=metric_name,
                        metric_value=value,
                        test_date=test_date
                    )
                    db.add(kpi_metric)
        
        db.commit()
        print("Seed data generated successfully!")
        print(f"- Test progress records: {len(test_progresses)}")
        print(f"- Bug records: 20")
        print(f"- KPI metric records: {len(models_list) * len(metrics) * 30}")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating seed data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize the database first.
    from backend.init_db import init_db
    init_db()
    
    # Generate sample data.
    seed_data()
