import csv
import glob

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

User = get_user_model()


class Command(BaseCommand):
    help = 'Укажите путь к папке с csv документами.'
    model_class_dict = {
        Ingredient.__name__.lower(): Ingredient,
        Tag.__name__.lower(): Tag
    }

    def add_arguments(self, parser):
        parser.add_argument('path_to_dir', type=str)

    def handle(self, *args, **options):
        csv_list = glob.glob(f'{options["path_to_dir"]}/*.csv')
        print(csv_list)
        pointer = 0
        if not csv_list:
            raise CommandError('В директории нет .csv файлов')
        while csv_list or pointer > len(csv_list):
            csv_file = csv_list[pointer]
            with open(csv_file, encoding='utf-8-sig') as file:
                file_name = csv_file.split('/')[-1]
                model_key = self._get_model_key_from_filename(file_name)
                if not model_key:
                    self.stdout.write(
                        f'Файл {file_name} не подходит ни к одной модели.',
                        ending='\n'
                    )
                    csv_list.pop(pointer)
                    continue
                model_class = self.model_class_dict[model_key]
                self._write_to_database(file, model_class)
                csv_list.pop(pointer)

    def _get_model_key_from_filename(self, file_name):
        for model_name in self.model_class_dict.keys():
            if model_name in file_name:
                return model_name
        return None

    def _write_to_database(self, file, model_class):
        reader = csv.reader(file)
        fields = []
        kwarg = {}
        if model_class is Ingredient:
            fields = Ingredient._meta.get_fields()[3:5]
        elif model_class is Tag:
            fields = Tag._meta.get_fields()[2:4]
        for row in reader:
            for i in range(len(row)):
                kwarg[fields[i].attname] = row[i]
            _, created = model_class.objects.get_or_create(**kwarg)
            self.stdout.write(
                f'Создан экземппляр модели {model_class.__name__}',
                ending='\n'
            )
