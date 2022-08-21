length = 1
def print_line(id, oid):
    print('id:{}, name:Testop_{}, type:Testop, identifier:Testop{}'.format(str(id), str(id), str(id)))
    print('\toutput nodes id:{}, type:Testop'.format(str(oid)))

for b in range(6):
    for i in range(length - 1):
        print_line(b*length + i, b*length + i + 1)


print_line(3 * length - 1, 6 * length)
print_line(4 * length - 1, 6 * length)
print_line(5 * length - 1, 6 * length)
print_line(6 * length, 5 * length)
print_line(1 * length - 1, 6 * length + 1)
print_line(2 * length - 1, 6 * length + 1)
print_line(6 * length - 1, 6 * length + 1)
print('id:{}, name:Testop_{}, type:Testop, identifier:Testop{}'.format(
                        str(6 * length + 1), str(6 * length + 1), str(6 * length + 1)))
print('id:{}, name:Testop_{}, type:Testop, identifier:Testop{}'.format(
                        str(6 * length + 2), str(6 * length + 2), str(6 * length + 2)))
print('\toutput nodes id:{}, type:Testop'.format(str(0 * length)))
print('\toutput nodes id:{}, type:Testop'.format(str(1 * length)))
print('\toutput nodes id:{}, type:Testop'.format(str(2 * length)))
print('\toutput nodes id:{}, type:Testop'.format(str(3 * length)))
print('\toutput nodes id:{}, type:Testop'.format(str(4 * length)))