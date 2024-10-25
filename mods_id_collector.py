import zipfile
import toml


class ModIdCollector:
    meta_path = 'META-INF/mods.toml'

    @classmethod
    def collect_mod_ids(cls, filepaths: [str]) -> [str]:
        return [
            mod_id for filepath in filepaths if cls.is_file_jar(filepath)
            for mod_id in [cls.extract_mod_id_from_jar(filepath)] if mod_id is not None
        ]

    @classmethod
    def is_file_jar(cls, filepath: str) -> bool:
        return filepath.endswith(".jar")

    @classmethod
    def extract_mod_id_from_jar(cls, filepath: str) -> str:
        with zipfile.ZipFile(filepath, 'r') as jar:
            if cls.meta_path in jar.namelist():
                with jar.open(cls.meta_path) as file:
                    return cls.find_mod_id(file)

    @classmethod
    def find_mod_id(cls, file):
        mods_data = toml.loads(file.read().decode('utf-8'))
        mods_list = mods_data.get('mods', [])
        if mods_list:
            return mods_list[0].get('modId')