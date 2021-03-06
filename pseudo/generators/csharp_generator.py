from pseudo.code_generator import CodeGenerator, switch
from pseudo.middlewares import DeclarationMiddleware, NameMiddleware
from pseudo.pseudo_tree import Node, local

class CSharpGenerator(CodeGenerator):
    '''CSharp code generator'''

    indent = 4
    use_spaces = True
    middlewares = [DeclarationMiddleware, 
                   NameMiddleware(
                       normal_name='camel_case', 
                       method_name='pascal_case',
                       function_name='pascal_case')]

    def params(self, node, indent):
        return ', '.join(
            '%s %s' % (
              self.render_type(node.pseudo_type[j + 1]), 
              self._generate_node(k)) for j, k in enumerate(node.params) )

    def anon_block(self, node, indent):
        if len(node.block) == 1:
            if node.block[0].type == 'implicit_return' or node.block[0].type == 'explicit_return':
                e = node.block[0].value
            else:
                e = node.block[0]    
            b = self._generate_node(e)
            return ' ' + b
        else:
            b = ';\n'.join(self.offset(indent + 1) + self._generate_node(e, indent + 1) for e in node.block) + ';\n'
            return '\n%s{\n%s%s}' % (self.offset(indent), b, self.offset(indent))

    types = {
      'Int': 'int',
      'Float': 'float',
      'Boolean': 'bool',
      'String': 'string',
      'List': 'List<{0}>',
      'Dictionary': 'Dictionary<{0}, {1}>',
      'Set': 'Set<{0}>',
      'Tuple': lambda x: 'Tuple<{0}>'.format(', '.join(x)),
      'Array': '{0}[]', 
      # fixed-size buffers in c# are not widely used
      # they require a struct and an unsafe annotation
      # we can a unsafe-fixed-size-buffer option to config
      'Void': 'void'
    }

    templates = dict(
        module     = '''
            %<dependencies:lines>
            %<custom_exceptions:lines>
            %<#class_definitions>
            public class Program
            {
                %<constants:lines>
                %<#function_definitions>
                public static void Main()
                {
                    %<main:semi>
                }
            }''',

        function_definition   = '''
            static %<@return_type> %<name>(%<#params>)
            {
                %<block:semi>
            }''',

        method_definition =     '''
            %<@return_type> %<name>(%<#params>)
            {
                %<block:semi>
            }''',

        class_definition = '''
            public class %<name>%<.base>
            {
                %<attrs:lines>
                %<.constructor>
                %<methods:line_join>
            }''',

        class_definition_base = ('%<#base>', ''),

        class_definition_constructor = ('%<constructor>', ''),

        class_attr = '%<.is_public>%<@pseudo_type> %<name>;',

        class_attr_is_public = ('public ', 'private '),
        
        anonymous_function = "%<params:join ', '> =>%<#anon_block>",

        constructor = '''
            %<this>(%<#params>)
            {
                %<block:semi>
            }''',

        dependency  = 'using %<name>;',


        local       = '%<name>',
        typename    = '%<name>',
        int         = '%<value>',
        float       = '%<value>',
        string      = '%<#safe_double>',
        boolean     = '%<value>',
        null        = 'null',

        list        = "new %<@pseudo_type> {%<elements:join ', '>}",
        dictionary  = "new %<@pseudo_type> { %<pairs:join ', '> }",
        pair        = "{%<key>, %<value>}",
        attr        = "%<object>.%<attr>",

        new_instance = "new %<class_name>(%<args:join ', '>)",

        assignment  = switch('first_mention',
            true       = 'var %<target> = %<value>', # in v0.3 add config/use var only for generic types
            _otherwise = '%<target> = %<value>'
        ),

        binary_op   = '%<left> %<op> %<right>',
        unary_op    = '%<op>%<value>',
        comparison  = '%<left> %<op> %<right>',

        static_call = "%<receiver>.%<message>(%<args:join ', '>)",
        call        = "%<function>(%<args:join ', '>)",
        method_call = "%<receiver>.%<message>(%<args:join ', '>)",

        this        = 'this',

        instance_variable = 'this.%<name>',

        throw_statement = 'throw new %<exception>(%<value>)',

        if_statement    = '''
            if (%<test>)
            {
                %<block:semi>
            }
            %<.otherwise>''',

        if_statement_otherwise = ('%<otherwise>', ''),

        elseif_statement = '''
            else if (%<test>)
            {
                %<block:semi>
            }
            %<.otherwise>''',

        elseif_statement_otherwise = ('%<otherwise>', ''),

        else_statement = '''
            else 
            {
                %<block:semi>
            }''',

        while_statement = '''
            while (%<test>)
            {
                %<block:semi>
            }''',

        try_statement = '''
            try
            {
                %<block:semi>
            }
            %<handlers:lines>''',

        exception_handler = '''
            catch (%<.exception> %<instance>)
            {
                %<block:semi>
            }''',

        exception_handler_exception = ('%<exception>', 'Exception'),

        for_each_statement = '''
            for %<iterator> in %<sequence>:
                %<#block>''',
    
        for_each_with_index_statement = '''
            for %<index>, %<iterator> in %<.sequence>:
                %<#block>''',

        for_each_with_index_statement_sequence = ('%<#index_sequence>', ''),

        for_each_in_zip_statement = '''
            for %<iterators:join ', '> in zip(%<sequences:join ', '>):
                %<#block>''',

        implicit_return = 'return %<value>',
        explicit_return = 'return %<value>',

        index            = '%<sequence>[%<index>]',

        index_assignment = '%<sequence>[%<index>] = %<value>',

        constant = '%<constant> = %<init>',

        regex = '@"%<value>',

        for_statement = switch(lambda f: f.iterators.type,
            for_iterator_with_index = '''
                for (int %<iterators.index> = 0; %<iterators.index> < %<sequences.sequence>.Count; %<iterators.index> ++)
                {
                    var %<iterators.iterator> = %<sequences.sequence>[%<iterators.index>];
                    %<block:semi>
                }''',

            for_iterator_zip = '''
                for (int _index = 0; _index < %<#first_sequence>.Count; _index ++)
                {
                    %<#zip_iterators>
                    %<block:semi>
                }''',

            for_iterator_with_items = '''
                foreach(var _item in %<sequences.sequence>)
                {
                    var %<iterators.key> = _item.key;
                    var %<iterators.value> = _item.value;
                    %<block:semi>
                }''',
            _otherwise = '''
                foreach(%<iterators> in %<sequences>)
                {
                    %<block:semi>
                }'''
        ),
        
        for_range_statement = '''
            for (int %<index> = %<.first>; %<index> != %<last>; %<index> += %<.step>)
            {
                %<block:semi>
            }''',

        for_range_statement_first = ('%<first>', '0'),

        for_range_statement_step = ('%<step>', '1'),

        for_iterator = 'var %<iterator>',

        for_iterator_zip = "var %<iterators:join ', '>",

        for_iterator_with_index = 'int %<index>, var %<iterator>',

        for_iterator_with_items = '%<key>, %<value>',

        for_sequence = '%<sequence>',

        custom_exception = '''
            public class %<name> : Exception
            {
                public %<name>(string message)
                    : base(message)
                {
                }
            }''',

        block = '%<block:semi>'
    )
    
    def class_definitions(self, node, depth):
        result = '\n'.join(self._generate_node(k) for k in node.definitions if k.type == 'class_definition')
        if result:
            return result + '\n'
        else:
            return ''

    def function_definitions(self, node, depth):
        result = '\n'.join(self._generate_node(f, 1) for f in node.definitions if f.type == 'function_definition')
        if result:
            return result + '\n'        
        else:
            return ''

    def base(self, node, depth):
        if node.base:
            return ' : %s' % node.base
        else:
            return ''

    def first_sequence(self, node, depth):
        return self._generate_node(node.sequences.sequences[0])

    def zip_iterators(self, node, depth):
        return '\n'.join(
            '%svar %s = %s;' % (
                self.offset(depth) if j else '',
                q.name,
                self._generate_node(
                    Node('index',
                        sequence=node.sequences.sequences[j],
                        index=local('_index', 'Int'),
                        pseudo_type=node.sequences.sequences[j].pseudo_type[1])))
            for j, q 
            in enumerate(node.iterators.iterators))
