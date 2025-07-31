import inspect
import logging
from typing import Callable, TypeVar, Any
from functools import wraps
from textual.case import camel_to_snake
from textual.message import Message

logger = logging.getLogger(__name__)


def _create_renamed_method_decorator(name_generator: Callable) -> Callable:
    """
    Factory function that creates a method renaming decorator.
    
    Args:
        name_generator: Function that takes the decorator arguments and returns the new method name
    """
    def decorator(*args):
        def inner_decorator(func):
            class RenamedMethod:
                def __init__(self, func):
                    self.func = func
                    self.new_name = name_generator(*args)
                    logger.debug(f"Rename {func.__name__} to {self.new_name} via {name_generator.__name__}")

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self.func
                    return self.func.__get__(obj, objtype)
                
                def __set_name__(self, owner, name):
                    # Rename the method in the class
                    setattr(owner, self.new_name, self.func)
                    if hasattr(owner, name):
                        delattr(owner, name)
            
            return RenamedMethod(func)
        return inner_decorator
    return decorator


def _message_name_generator(cls: type) -> str:
    """Generate handler name for message decorator."""
    return cls.handler_name


def _action_name_generator(name: str) -> str:
    """Generate action name for action decorator."""
    return f"action_{name}"


def _watch_name_generator(name: str) -> str:
    """Generate watch name for watch decorator."""
    return f"watch_{name}"


# Create the three decorators using the factory
message = _create_renamed_method_decorator(_message_name_generator)
action = _create_renamed_method_decorator(_action_name_generator)
watch = _create_renamed_method_decorator(_watch_name_generator)




# Test section
if __name__ == "__main__":
    from pprint import pprint



    class LdapEntrySelection(Message):
        """Message sent when an LDAP entry is selected in the tree."""

        def __init__(self, tree_view, node_data: dict):
            # assert False
            self.tree_view = tree_view
            self.node_data = node_data
            super().__init__()


    class Parent():
        "Parent class for testing"

        class LdapEntrySelection2(Message):
            """Message sent when an LDAP entry is selected in the tree."""

            def __init__(self, tree_view, node_data: dict):
                # assert False
                self.tree_view = tree_view
                self.node_data = node_data
                super().__init__()




    # class TestClass():
    #     pass
    
    # Test class with individual method decorators
    class TestClass2:

        @message(LdapEntrySelection)
        def get_data1(self) -> str:
            return "data"
        
        @message(Parent.LdapEntrySelection2)
        def get_data2(self) -> str:
            return "data"

        def normal_method(self) -> str:
            return "normal"
        

    pprint(TestClass2.__dict__)
    
    # Test the decorators
    def test_rename_method():
        # Test class decorator
        
        # Test individual method decorator
        obj2 = TestClass2()
        
        # Check that specific method is renamed
        assert hasattr(obj2, "on_ldap_entry_selection")
        assert not hasattr(obj2, "get_data")
        
        assert hasattr(obj2, "on_parent_ldap_entry_selection2")
        assert not hasattr(obj2, "get_data2")
        

        # Check that other methods are not affected
        assert hasattr(obj2, "normal_method")
        
        # Test functionality
        assert obj2.on_ldap_entry_selection() == "data" # pylint: disable=no-member
        assert obj2.on_parent_ldap_entry_selection2() == "data" # pylint: disable=no-member
        assert obj2.normal_method() == "normal"
        
        print("✅ All tests passed!")

    
    test_rename_method()


