import os
import re
import csv
import codecs
import sys
from typing import List

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError

from reviews import models
from core.exceptions.import_csv import (UnexpectedFile, DoesNotExistFunction,
                                        DataAlreadyExist, NotSetStaticfilesDir,
                                        NotFoundPath)


class Command(BaseCommand):
    help = 'Импорт данных в БД.'
    data_path = None

    _MODELS_OR_LINKS = {
        'users.csv': {
            'model': models.User,
            'type': 'model',
            'data': []
        },
        'category.csv': {
            'model': models.Category,
            'type': 'model',
            'data': []
        },
        'genre.csv': {
            'model': models.Genre,
            'type': 'model',
            'data': []
        },
        'titles.csv': {
            'model': models.Title,
            'type': 'model',
            'data': []
        },
        'review.csv': {
            'model': models.Review,
            'type': 'model',
            'data': []
        },
        'comments.csv': {
            'model': models.Comment,
            'type': 'model',
            'data': []
        },
        'genre_title.csv': {
            'model': 'Genre_Title',
            'type': 'link',
            'parent': models.Title,
            'data': []
        }
    }

    _INDEX_STATICFILES_DIRS = 0
    _SYS_EXIT_CODE = 1

    def parse_file(self, path: str, file_name: str) -> None:
        """Формирует из файла массив для записи."""
        if self._MODELS_OR_LINKS.get(file_name) is None:
            raise UnexpectedFile('Непредвиденный файл: ', file_name)
        with codecs.open(f'{path}/{file_name}', 'r', 'utf_8_sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self._MODELS_OR_LINKS[file_name]['data'].append(row)

    def _prepare_row(self, value: dict) -> dict:
        """Подготовка данных к записи."""
        if value.get('category'):
            value['category'] = models.Category.objects.get(
                pk=value['category'])
        if value.get('author'):
            value['author'] = models.User.objects.get(pk=value['author'])
        return value

    def _model_base(self, model_: dict) -> None:
        """Запись данных в БД."""
        model_['model'].objects.bulk_create(
            [model_['model'](**self._prepare_row(row)) for row in
             model_['data']],
            ignore_conflicts=True)

    def model_genre_title(self, model_: dict) -> None:
        """Создание связей многие ко многим для моделей Genre и Title."""
        for raw in model_['data']:
            title_id = raw['title_id']
            genre_id = raw['genre_id']
            title = models.Title.objects.get(pk=title_id)
            title.genre.add(
                models.Genre.objects.get(pk=genre_id)
            )

    def write_db(self) -> None:
        """Вызов функций записи в БД."""
        for model_ in self._MODELS_OR_LINKS.values():
            # В зависимости от модели запускается определенная функция.
            func_name = '_model_base'
            if model_['type'] == 'custom_model':
                func_name = f'model_{model_["model"].__name__.lower()}'
            if model_['type'] == 'link':
                func_name = f'model_{model_["model"].lower()}'
            try:
                func = getattr(self, func_name)
                func(model_)
            except AttributeError:
                raise DoesNotExistFunction(func_name, 'не определена.')
            except IntegrityError:
                raise DataAlreadyExist(model_['model'],
                                       'данные уже существуют в бд')

    def get_data_path(self) -> str:
        """Формирует путь к каталогу с csv файлами."""
        if self.data_path is None:
            if len(settings.STATICFILES_DIRS) < 1:
                raise NotSetStaticfilesDir(
                    'Не задан путь для статических файлов.')
            path = settings.STATICFILES_DIRS[self._INDEX_STATICFILES_DIRS]
            return path + 'data/'
        return self.data_path

    def validate_dir(self, path: str) -> None:
        """Проверка наличия каталога."""
        if not os.path.isdir(path):
            raise NotFoundPath('Не найден каталог: ', path)

    def get_csv_files(self, path: str) -> List[str]:
        """Формирование списка csv файлов."""
        files = os.listdir(path)
        csv_files = []
        for file in files:
            csv_file = re.fullmatch(r'^.+\.csv$', file)
            if csv_file:
                csv_files.append(csv_file[0])
        return csv_files

    def handle(self, *args, **options):
        try:
            path = self.get_data_path()
            self.validate_dir(path)
            files = self.get_csv_files(path)
            for file in files:
                self.parse_file(path, file)
            self.write_db()
        except UnexpectedFile as error:
            print(error)
        except DoesNotExistFunction as error:
            print(error)
        except DataAlreadyExist as error:
            print(error)
        except NotSetStaticfilesDir as error:
            print(error)
            sys.exit(self._SYS_EXIT_CODE)
        except NotFoundPath as error:
            print(error)
            sys.exit(self._SYS_EXIT_CODE)
