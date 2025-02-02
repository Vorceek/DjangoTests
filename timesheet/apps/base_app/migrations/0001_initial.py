# Generated by Django 5.0.6 on 2025-02-02 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atividade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('setor', models.ManyToManyField(blank=True, related_name='atividades', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('atividades', models.ManyToManyField(blank=True, related_name='servicos', to='base_app.atividade')),
                ('setor', models.ManyToManyField(blank=True, related_name='servico', to='auth.group')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('setor', models.ManyToManyField(blank=True, related_name='cliente', to='auth.group')),
                ('servicos', models.ManyToManyField(blank=True, related_name='clientes', to='base_app.servico')),
            ],
        ),
    ]
