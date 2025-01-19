import os
import pandas as pd
from django.apps import AppConfig
from django.db.utils import OperationalError


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        init_skills_table()


def init_skills_table():
    # Delayed import (after loading Django app)
    from users.models import Skill

    file_path = os.path.join(os.path.dirname(__file__), "../skills.csv")

    try:
        any_skill = Skill.objects.all()[0]
    except IndexError:
        try:
            skills_data = pd.read_csv(file_path)
            for skill in skills_data["name"]:
                new_skill = Skill.objects.create(name=skill)
                new_skill.save()
        except OperationalError:
            print("Error during database init operation")
    except OperationalError:
        pass
