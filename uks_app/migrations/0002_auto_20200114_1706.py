# Generated by Django 3.0.2 on 2020-01-14 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('uks_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('description', models.TextField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='MilestoneChange',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='uks_app.Event')),
                ('title', models.CharField(max_length=200)),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=200)),
                ('checkpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uks_app.Milestone')),
            ],
            bases=('uks_app.event',),
        ),
        migrations.RemoveField(
            model_name='checkpointchange',
            name='checkpoint',
        ),
        migrations.RemoveField(
            model_name='checkpointchange',
            name='event_ptr',
        ),
        migrations.AddField(
            model_name='issue',
            name='description',
            field=models.TextField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='issue',
            name='state',
            field=models.CharField(choices=[('OP', 'Open'), ('CL', 'Closed')], default='OP', max_length=2),
        ),
        migrations.AddField(
            model_name='observedproject',
            name='description',
            field=models.TextField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='statechange',
            name='newState',
            field=models.CharField(choices=[('OP', 'Open'), ('CL', 'Closed')], default='OP', max_length=6),
        ),
        migrations.DeleteModel(
            name='Checkpoint',
        ),
        migrations.DeleteModel(
            name='CheckpointChange',
        ),
        migrations.AddField(
            model_name='milestone',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uks_app.ObservedProject'),
        ),
    ]
