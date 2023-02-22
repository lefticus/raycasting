import abc
import dataclasses
from typing import Dict, List, Self

@dataclasses.dataclass
class TypeHint():
    members_to_serialize: List[str] = dataclasses.field(default_factory=lambda: ([]))

@dataclasses.dataclass
class SerializeObject():
    object: object
    type: type
    typename: str
    annotations: Dict

    def __eq__(self: Self, __o: object) -> bool:
        if isinstance(__o, SerializeObject):
            return self.type == __o.type or self.typename == __o.typename
        if isinstance(__o, str):
            return self.typename == __o
        return False

    def __str__(self: Self) -> str:
        return self.typename

    @classmethod
    def from_object(cls, object: object, annotations: Dict) -> Self:
        object_type = type(object)
        return SerializeObject(
            object=object,
            type=object_type,
            typename=object_type.__name__,
            annotations=annotations,
        )

@dataclasses.dataclass
class Context():
    output: SerializeObject
    input: SerializeObject
    member: str
    serializer: object

class TypeHandler(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def typename(cls) -> str:
        raise NotImplemented()
    
    @classmethod
    @abc.abstractmethod
    def serialize(cls, context: Context):
        raise NotImplemented()
    
    @classmethod
    @abc.abstractmethod
    def deserialize(cls, context: Context):
        raise NotImplemented()
    
    def __eq__(self, other: object) -> bool:
        return self.typename() == other

class PrimitiveTypeHandler(TypeHandler):
    @classmethod
    def serialize(cls, context: Context):
        context.output.object = context.input.object

    @classmethod
    def deserialize(cls, context: Context):
        context.output.object = context.input.object

class StringHandler(PrimitiveTypeHandler):
    @classmethod
    def typename(cls) -> str:
        return "str"
    
class IntegerHandler(PrimitiveTypeHandler):
    @classmethod
    def typename(cls) -> str:
        return "int"
    
class BooleanHandler(PrimitiveTypeHandler):
    @classmethod
    def typename(cls) -> str:
        return "bool"
    
class FloatHandler(PrimitiveTypeHandler):
    @classmethod
    def typename(cls) -> str:
        return "float"
    
class ListHandler(TypeHandler):
    @classmethod
    def typename(cls) -> str:
        return "list"
    
    @classmethod
    def serialize(cls, context: Context):
        context.output.object = []
        for data in context.input.object:
            context.output.object.append(context.serializer.serialize(data))

    @classmethod
    def deserialize(cls, context: Context):
        if context.output.annotations is None:
            return
        
        type = context.output.annotations.__args__[0]
        for data in context.input.object:
            new = type()
            context.serializer.deserialize(new, data)
            context.output.object.append(new)

class Methods(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def determining_object(cls, context: Context) -> SerializeObject:
        raise NotImplemented()
    
    @classmethod
    @abc.abstractmethod
    def auto(cls, context: Context):
        raise NotImplemented()
    
    @classmethod
    @abc.abstractmethod
    def member(cls, context: Context):
        raise NotImplemented()

    @classmethod
    @abc.abstractmethod
    def handler(cls, context: Context, handler: TypeHandler):
        raise NotImplemented()

class SerializeMethods(Methods):
    @classmethod
    def determining_object(cls, context: Context) -> SerializeObject:
        return context.input

    @classmethod
    def auto(cls, context: Context):
        data = getattr(context.input.object, context.member)
        if not callable(data):
            context.output.object[context.member] = context.serializer.serialize(
                data,
                annotations = context.output.annotations
            )

    @classmethod
    def member(cls, context: Context):
        assert(hasattr(context.input.object, context.member))
        context.output.object[context.member] = context.serializer.serialize(
            getattr(context.input.object, context.member),
            annotations = context.output.annotations
        )

    @classmethod
    @abc.abstractmethod
    def handler(cls, context: Context, handler: TypeHandler):
        handler.serialize(context)

class DeserializeMethods(Methods):
    @classmethod
    def determining_object(cls, context: Context) -> SerializeObject:
        return context.output
    
    @classmethod
    def auto(cls, context: Context):
        data = getattr(context.output.object, context.member)
        if not callable(data) and context.member in context.input.object:
            context.serializer.deserialize(
                data,
                context.input.object[context.member],
                annotations = context.input.annotations
            )

    @classmethod
    def member(cls, context: Context):
        assert(hasattr(context.output.object, context.member))
        setattr(
            context.output.object,
            context.member,
            context.serializer.deserialize(
                getattr(context.output.object, context.member),
                context.input.object[context.member],
                annotations = context.output.annotations
            )
        )

    @classmethod
    @abc.abstractmethod
    def handler(cls, context: Context, handler: TypeHandler):
        handler.deserialize(context)

class Serializer():
    DefaultHandlers = [
        StringHandler(),
        IntegerHandler(),
        BooleanHandler(),
        FloatHandler(),
        ListHandler()
    ]
    SerializeMethods = SerializeMethods
    DeserializeMethods = DeserializeMethods

    def __init__(self, hints: Dict[str, TypeHint] = {}, handlers: List[TypeHandler] = DefaultHandlers):
        self.__hints = hints
        self.__handlers = handlers
        self.__recursion = 0

        for _, hint in hints.items():
            assert isinstance(hint, TypeHint)
        
        for handler in handlers:
            assert issubclass(type(handler), TypeHandler)

    def serialize(self, data: object, annotations: Dict = None) -> object:
        output = {}
        return self.__process__(self.__get_context__(output, data, None, annotations, self), self.SerializeMethods)

    def deserialize(self, object: object, data: object, annotations: Dict = None) -> object:
        return self.__process__(self.__get_context__(object, data, None, annotations, self), self.DeserializeMethods)
    
    def __process__(self, context: Context, methods: Methods) -> object:
        assert self.__recursion >= 0
        assert self.__recursion <= 10
        self.__recursion += 1

        determining_object = methods.determining_object(context)
        if determining_object.typename in self.__handlers:
            methods.handler(context, self.__handlers[self.__handlers.index(determining_object.typename)])
        elif determining_object.typename in self.__hints:
            self.__member__(self.__hints[determining_object.typename], context, methods)
        else:
            self.__auto__(context, methods)

        self.__recursion -= 1
        return context.output.object

    def __auto__(self, context: Context, methods: Methods):
        determining_object = methods.determining_object(context)
        has_annotations = hasattr(determining_object.object, "__annotations__")
        attributes = determining_object.object.__annotations__ if has_annotations else vars(determining_object.object)
        for member in attributes:
            if (member[:2] == '__' and member[-2:] == '__') or member[:1] == '_':
                continue

            methods.auto(
                self.__get_context__(
                    context.output.object,
                    context.input.object,
                    member,
                    attributes[member] if has_annotations else None,
                    self
                )
            )
            
    def __member__(self, hint: TypeHint, context: Context, methods: Methods):
        for member in hint.members_to_serialize:
            methods.member(self.__get_context__(context.output.object, context.input.object, member, None, self))
    
    @classmethod
    def __get_context__(cls, output: object, input:object, member: str, annotations: Dict, serializer: object) -> Context:
        return Context(
            output=SerializeObject.from_object(output, annotations),
            input=SerializeObject.from_object(input, annotations),
            member=member,
            serializer=serializer,
        )