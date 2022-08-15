import os
import re
from typing import List

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Импорт данных в БД.'
    data_path = None

    def get_data_path(self) -> str:
        """Формирует путь к каталогу с csv файлами."""
        if self.data_path is None:
            if len(settings.STATICFILES_DIRS) < 1:
                raise ValueError()
            path = settings.STATICFILES_DIRS[0]
            return path + 'data/'
        return self.data_path

    def validate_dir(self, path: str) -> None:
        """Проверка наличия каталога."""
        if not os.path.isdir(path):
            raise ValueError()

    def get_csv_files(self, path: str) -> List[str]:
        """Формирование списка csv файлов."""
        files = os.listdir(path)
        csv_files = []
        for file in files:
            csv_file = re.fullmatch(r'^.+\.csv$', file)
            if csv_file: csv_files.append(csv_file[0])
        return csv_files

    def handle(self, *args, **options):
        path = self.get_data_path()
        self.validate_dir(path)
        files = self.get_csv_files(path)
        print(files)