from typing import Callable, Dict, Type


class MappingCollection:
    def __init__(self):
        self.storage: Dict[str, Callable] = {}
        self.code: Dict[str, str] = {}

    def __getitem__(self, key: str) -> Callable:
        return self.storage[key]

    def get_create_func(self, SourceCls: Type, TargetCls: Type) -> Callable:
        func = self.storage.get(self.create_func_name(SourceCls, TargetCls))
        if not func:
            raise NotImplementedError(
                f"Object of type '{SourceCls.__name__}' cannot be mapped to '{TargetCls.__name__}'"
            )
        return func

    def get_update_func(self, SourceCls: Type, TargetCls: Type) -> Callable:
        func = self.storage.get(self.update_func_name(SourceCls, TargetCls))
        if not func:
            raise NotImplementedError(
                f"Object of type '{SourceCls.__name__}' cannot be mapped to '{TargetCls.__name__}'"
            )
        return func

    def get_create_code(self, SourceCls: Type, TargetCls: Type) -> str:
        code = self.code.get(self.create_func_name(SourceCls, TargetCls))
        if not code:
            raise NotImplementedError(
                f"Object of type '{SourceCls.__name__}' cannot be mapped to '{TargetCls.__name__}'"
            )
        return code

    def get_update_code(self, SourceCls: Type, TargetCls: Type) -> str:
        code = self.code.get(self.update_func_name(SourceCls, TargetCls))
        if not code:
            raise NotImplementedError(
                f"Object of type '{SourceCls.__name__}' cannot be mapped to '{TargetCls.__name__}'"
            )
        return code

    def contains_create(self, SourceCls: Type, TargetCls: Type) -> bool:
        return self.create_func_name(SourceCls, TargetCls) in self.storage

    def contains_update(self, SourceCls: Type, TargetCls: Type) -> bool:
        return self.update_func_name(SourceCls, TargetCls) in self.storage

    def store_create_func(
        self, SourceCls: Type, TargetCls: Type, func: Callable, code: str, factories: Dict[str, Callable]
    ) -> None:
        if self.contains_create(SourceCls, TargetCls):
            raise AttributeError(
                f"There already exists a mapping between '{SourceCls.__name__}' and '{TargetCls.__name__}'"
            )
        self.storage[self.create_func_name(SourceCls, TargetCls)] = func
        self.code[self.create_func_name(SourceCls, TargetCls)] = code
        for name, factory in factories.items():
            self.storage[name] = factory

    def store_update_func(
        self, SourceCls: Type, TargetCls: Type, func: Callable, code: str, factories: Dict[str, Callable]
    ) -> None:
        if self.contains_update(SourceCls, TargetCls):
            raise AttributeError(
                f"There already exists a mapping between '{SourceCls.__name__}' and '{TargetCls.__name__}'"
            )
        self.storage[self.update_func_name(SourceCls, TargetCls)] = func
        self.code[self.update_func_name(SourceCls, TargetCls)] = code
        for name, factory in factories.items():
            self.storage[name] = factory

    def cls_to_name(self, cls: Type) -> str:
        try:
            identifier = f"{cls.__name__}_{id(cls)}"
            return identifier
        except AttributeError as exc:
            raise TypeError("Bad Type") from exc

    def create_func_name(self, SourceCls: Type, TargetCls: Type) -> str:
        return f"{self.cls_to_name(SourceCls)}__mapcreate_to__{self.cls_to_name(TargetCls)}"

    def update_func_name(self, SourceCls: Type, TargetCls: Type) -> str:
        return f"{self.cls_to_name(SourceCls)}__mapupdate_to__{self.cls_to_name(TargetCls)}"


COLLECTION = MappingCollection()
