import unittest
import textwrap
from pseudo import generate
from pseudo.pseudo_tree import Node
import suite as suite

def dedent_with_tabs(source):
    a = textwrap.dedent(source)
    return a.replace('    ', '\t')

#v
class TestGo(unittest.TestCase, metaclass=suite.TestLanguage): # dark magic bitches

    _language = 'go'
    _import = 'import'

    def gen(self, custom_exceptions, ast):
        imports, source = self.gen_with_imports(custom_exceptions, ast)
        return source.strip()


    def gen_special(self, source):
        lines = source.split('\n')
        main_index = lines.index('func main() {')
        main = '\n'.join([line[1:] for line in lines[main_index + 1:-2]]).strip()
        l = 0

        if lines[0].startswith('import'):
            if lines[0][7] == '"':
                imports = {lines[0][8:-1]}
                m = 1
            else:
                m = lines.index(')')
                imports = {line.strip()[1:-1] for line in lines[1:m]}
            definitions = '\n'.join(lines[m + 1:main_index])
        else:
            imports = set()
            definitions = '\n'.join(lines[:main_index])
        return imports, definitions + main

    # make declarative style great again

    # expected go translation for each example in suite:

    int_ = '42'

    float_ = '42.42'

    string = '"la"'

    null = 'nil'

    dictionary = 'map[string]int { "la": 0 }'

    list_ = '[]string {"la"}'

    local = 'egg'

    typename = 'Egg'

    instance_variable = 'this.egg'

    attr = 'e.egg'

    local_assignment = 'egg = ham'

    instance_assignment = 'this.egg = ham'

    attr_assignment = 'T.egg = ham'

    call = 'map(x)'

    method_call = 'e.filter(42)'

    standard_call = [
        ({'fmt'}, 'fmt.Println(42)'),
        ({'bufio', 'os'}, dedent_with_tabs('''\
            reader, err := bufio.NewReader(os.Stdin)
            reader.ReadString("\\n")''')),
        ({'math'}, 'Math.Log(ham)'),
        ({'io/ioutil'}, 'source := ioutil.ReadFile("f.py")')
    ]

    standard_method_call = [
        'len(l)',
        '"l"[0:2]',

        # #

        # 'cpus = append(cpus, planet)', #cpus.push(planet)
        # 'planet, cpus = cpus[len(cpus) - 1], cpus[:len(cpus) - 1]' # planet = cpus.pop()
        # 'len(cpus)', # cpu.length
        # dedent_with_tabs('''\
        #     cpus = append(cpus, 0)
        #     copy(cpus[x + 1:], cpus[x:])
        #     cpus[x] = planet
        #     '''), # cpu.insert_at(planet, x)
        # 'cpus = append([]int{planet}, cpus...)', # cpu.unshift(planet)
        # 'planet, cpus := cpus[0], cpus[1:]', # planet = cpu.shift()
        # 'cpus = append(cpus[:x], cpus[x + 1:]...)', # cpus.remove_at(x)
        # 'starfleet := cpus[2:4]', # starfleet = cpus[2:4]
        # 'starfleet := cpus[x:]', # starfleet = cpus[x:]
        # dedent_with_tabs('''\
        #     repeated_cpus := cpus
        #     for _ := range(3) {
        #         repeated_cpus = append(repeated_cpus, cpus)
        #     }                
        #     sh(repeated_cpus)
        #     '''), # sh(cpus * 4)
        # dedent_with_tabs('''\
        #     found := -1
        #     for as_index, as_element := range as {
        #         if as_element == query {
        #             found := as_index
        #             break
        #         }
        #     }
        #     sh(found, 2)
        #     '''), # sh(as.find(query), 2)
        # (['strings'],
        #  'sh(2, strings.Join(cpus, "\n"))'), # sh(2, '\n'.join(cpus))

        # dedent_with_tabs('''\
        #     reversed_cpus := make([]int, len(cpus))
        #     for cpus_index, cpus_element := range len(cpus) {
        #         reversed_cpus[len(cpus) - cpus_index - 1] = cpus_element
        #     }
        #     sh(reversed_cpus)
        #     '''), # sh(cpus.reverse())


        # # Dictionary

        # dedent_with_tabs('''
        #     cpus_keys := make([]int, len(cpus))
        #     cpus_index := 0
        #     for cpus_key, _ := range cpus {
        #         cpus_keys[cpu_index] = cpus_key
        #         cpus_index += 1
        #     }
        #     sh(cpus_keys[:2])
        #     '''), # sh(cpu.keys()[:2])

        # dedent_with_tabs('''
        #     cpus_values := make([]int, len(cpus))
        #     cpus_index := 0
        #     for _, cpus_value := range cpus {
        #         cpus_values[cpus_index] = cpus_key
        #         cpus_index += 1
        #     }
        #     sh(cpus_keys[4])
        #     '''),

        # 'len(cpus)',

        # # String

        # 'name[i:j]',
        # 'name[i:]',
        # 'name[:j + h()]',
        # 'len(name)',
        # (['strings'],
        # 'strings.Index(name, help)'), # name.find(help)
        # (['strings'],
        # 'strings.Count(name, help)'), # name.count(help)
        # (['fmt'],
        # 'fmt.Println("wow %s", wtf)'), # print('wow %s' % wtf)
        # (['strings'],
        # 'strings.Repeat(name, count)'),  # name * count
        # (['buffer', 'fmt'],
        # dedent_with_tabs('''
        #     var buffer bytes.Buffer
        #     for h := cpus {
        #         buffer.writeString(h)
        #         buffer.writeString(" h")
        #     }
        #     ''')), # buffer = [h + ' h' for h in cpus]
        # (['strings'],
        #   's.Trim("Achtung !!!  ", " ")'), # 'Achtung !!!  '.strip() 
        # (['strings'],
        #   's.Split(help)'), # s.split(help)
        # (['strings'],
        #  dedent_with_tabs('''
        #     result := s.SplitN(help, 2)'
        #     separator := help            
        #     b := result[1]
        #     sh(separator, b)
        #     ''')), # _, separator, b = s.partition(help)
        #            # sh(separator, b)

    ]

    binary_op = 'ham + egg'

    unary_op = '-a'

    comparison = 'egg > ham'

    if_statement = (
        {'fmt'},
        dedent_with_tabs('''\
            if egg == ham {
                l[0:2]
            } else if egg == ham {
                fmt.Println(4.2)
            } else {
                z
            }''')
    )
    


    for_statement = [
        dedent_with_tabs('''\
            for _, a := range sequence {
                log(a)
            }'''),
        dedent_with_tabs('''\
            for j := 0; j != 42; j += 2 {
                analyze(j)
            }'''),
        dedent_with_tabs('''\
            for j, k := range z {
                analyze(j, k)
            }'''),
        dedent_with_tabs('''\
            for j, k := range z {
                analyze(k, j)
            }'''),
        dedent_with_tabs('''\
            for _index, _ := range len(z) {
                k := z[_index]
                l := zz[_index]
                a(k, l)
            }''')
    ]

    while_statement = dedent_with_tabs('''\
        for f() >= 42 {
            b := g()
        }''')

    function_definition = dedent_with_tabs('''\
        func weird(z int) int {
            fixed := fix(z)
            return fixed
        }''')

    method_definition = (
        dedent_with_tabs('''\
            func parse(this *A, source string) []string {
                this.ast = 0
                return []string {source}
            }'''))

    anonymous_function = [
        'func (source string) { return ves(len(source)) }',

        dedent_with_tabs('''\
            func (source string) {
                fmt.Println(source)
                return ves(len(source))
            }''')
    ]

    class_statement = [dedent_with_tabs('''\
        struct A {
            a int
        }

        func parse(this *A) int {
            return 42
        }''')]

    this = 'this'

    go_constructor = textwrap.dedent('''\
        struct A {
            z int
        }

        func newA(a int, b int) *A {
          return A{a + b}
        }''')

    index = '"la"[2]'

    # try_statement = [
    #     textwrap.dedent('''\
    #         result, err := h(-4)
    #         if err != nil {
    #             fmt.Printf("%s", err)
    #             return 0
    #         } else {
    #             result += 2
    #         }
    #         return x(result)
    #         '''),

    #     textwrap.dedent('''\
    #         type NeptunError struct {
    #             s string
    #         }

    #         func (this *NeptunError) Error() string {
    #             return this.s
    #         }

    #         result, err := h(-4)
    #         if _err, ok := err.(*NeptunError); ok {
    #             fmt.Printf("%s", err)
    #             return 0
    #         } else {
    #             result += 2
    #         }
    #         return x(result)
    #         ''')
    # ]

    # throw_statement = textwrap.dedent('''\
    #     type NeptunError struct {
    #         s string
    #     }

    #     func (this *NeptunError) Error() string {
    #         return this.s
    #     }
        
    #     func h(s int) (int, error) {
    #         if s > 0 {
    #             return 0, &NeptunError{"no tea"}
    #         }
    #         return -s
    #     }
    #     ''')



    