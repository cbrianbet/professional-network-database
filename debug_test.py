import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.append('/Users/charlesbett/Source/professional-network-database')
django.setup()

# Import the test functions from sprint2_qa_test
from sprint2_qa_test import (
    test_file_resource_model,
    test_pending_user_status,
    test_login_blocks_pending_users,
    test_admin_user_management_enhancements,
    test_admin_stats_endpoint,
    test_admin_user_approve_reject
)

tests = [
    ("FileResource model", test_file_resource_model),
    ("Pending user status", test_pending_user_status),
    ("Login blocking pending users", test_login_blocks_pending_users),
    ("Admin user management enhancements", test_admin_user_management_enhancements),
    ("Admin stats endpoint", test_admin_stats_endpoint),
    ("Admin user approve/reject", test_admin_user_approve_reject)
]

for name, test_func in tests:
    print(f"\n=== Running {name} ===")
    try:
        if test_func():
            print(f"✓ {name} passed")
        else:
            print(f"✗ {name} returned False")
    except Exception as e:
        print(f"✗ {name} raised exception: {e}")
        traceback.print_exc()
