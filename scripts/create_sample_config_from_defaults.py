import re

regex = re.compile(r'^()$', re.MULTILINE)

with open('psiturk/default_configs/local_config_defaults.txt', 'r') as f:
    lines = f.readlines()

new_lines = []
line_num = 0
for line in lines:
    if line_num == 2:
        line = (
            f'# Example config file. Uncomment lines (remove the `;`)\n'
            f'# in order to override defaults.\n'
        )
    if len(line) > 1 and line[0] not in ['#','[']: # every line will have at least an \n char
        line = f';{line}'
    new_lines.append(line)
    line_num += 1

with open('psiturk/example/config.txt.sample','w') as f:
    f.writelines(new_lines)
