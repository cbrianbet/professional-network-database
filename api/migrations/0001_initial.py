from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password_hash', models.TextField()),
                ('role', models.TextField(choices=[('user', 'User'), ('admin', 'Admin')], default='user')),
                ('status', models.TextField(choices=[('active', 'Active'), ('pending', 'Pending'), ('disabled', 'Disabled')], default='active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'users', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='api.user')),
                ('name', models.TextField()),
                ('phone', models.TextField()),
                ('email', models.TextField()),
                ('age', models.IntegerField()),
                ('national_id', models.TextField()),
                ('sub_location', models.TextField(blank=True, default='')),
                ('education', models.TextField(blank=True, default='')),
                ('form_four_year', models.IntegerField(blank=True, null=True)),
                ('kcse', models.TextField(blank=True, default='')),
                ('institution', models.TextField(blank=True, default='')),
                ('course', models.TextField(blank=True, default='')),
                ('graduation', models.IntegerField(blank=True, null=True)),
                ('status', models.TextField()),
                ('employer', models.TextField(blank=True, default='')),
                ('career', models.TextField(blank=True, default='')),
                ('skills', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'members', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='api.user')),
                ('full_name', models.TextField()),
                ('email', models.TextField()),
                ('headline', models.TextField(blank=True, default='')),
                ('location', models.TextField(blank=True, default='')),
                ('skills', models.JSONField(blank=True, default=list)),
                ('summary', models.TextField(blank=True, default='')),
                ('status', models.TextField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'profiles', 'ordering': ['-created_at']},
        ),
    ]
