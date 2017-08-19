#!/usr/bin/env python3
# Author: He Yingqin

import datetime
import os
import getpass
import shelve

color_red = '\033[1;31m'  # 红色加粗字体，用于显示错误类提示信息
color_green = '\033[1;32m'  # 绿色加粗字体，用于显示成功类提示信息
color_yellow = '\033[1;33m'  # 黄色加粗字体，用于显示功能菜单
color_end = '\033[0m'  # 颜色结束符

main_menu = '''
%s**************
1.用户注册
2.用户登录
3.退出程序
**************%s
''' % (color_yellow, color_end)  # 程序运行时显示的主菜单

user_login_menu = '''
%s************
1.修改密码
2.返回主菜单
3.退出程序
************%s
''' % (color_yellow, color_end)  # 普通用户登录成功后显示的子菜单

admin_login_menu = '''
%s**************
1.修改密码
2.用户删除
3.用户解锁
4.查看用户信息
5.返回主菜单
6.退出程序
**************%s
''' % (color_yellow, color_end)  # 管理员登录成功后显示的子菜单


def timestamp():
    # 生成一个"yyyy-mm-dd HH:MM:SS"格式的日期字符串
    register_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return register_time


def user_info_file_check():
    # 判断用户信息文件.user_info.db是否存在，不存在则创建，并添加管理员用户
    if not os.path.exists('.user_info.db'):
        with shelve.open('.user_info') as user_info:
            user_info['administrator'] = {'password': 'administrator', 'status': 'unlock', 'register_time': timestamp()}


def user_choice_check(user_choice, *args):
    # 判断用户输入的选择是否正确
    while True:
        if user_choice not in args:
            user_choice = input('%s您的输入有误，请重新输入：%s' % (color_red, color_end)).strip()
        else:
            return user_choice


def user_register_username_check(username):
    # 普通用户注册时，对username做检验
    with shelve.open('.user_info') as user_info:
        while True:
            if username == 'q' or username == 'Q':
                break
            elif username in user_info:  # 判断username是否存在
                username = input('%s用户名已存在，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
            elif not username.isalnum():  # 判断username是否只包含字母和数字
                username = input('%s用户名只能是字母与数字的组合，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
            elif not 6 <= len(username) <= 15:  # 判断username长度是否为6~15个字符
                username = input('%s用户名长度为6~15个字符，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
            else:
                return username


def user_login_username_check(username):
    # 普通用户登录时，对username做校验
    with shelve.open('.user_info') as user_info:
        while True:
            if username == 'q' or username == 'Q':
                break
            elif username not in user_info:  # 判断username是否不存在
                username = input('%s用户名不存在，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
            elif user_info[username]['status'] == 'lock':  # 判断username是否存在，且为'lock'状态
                username = input('%s该用户已被锁定，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
            else:
                return username


def password_check(password):
    # 对用户输入的password做校验
    while True:
        if password == 'q' or password == 'Q':
            break
        elif not password.isalnum():  # 判断password是否只包含字母和数字
            password = getpass.getpass('%s密码只能是字母与数字的组合，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
        elif not 6 <= len(password) <= 15:  # 判断password长度是否为6~15个字符
            password = getpass.getpass('%s密码长度为6~15个字符，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
        else:
            return password


def login_status_check(username, password):
    with shelve.open('.user_info', writeback=True) as user_info:
        count = 1
        while True:
            if password == 'q' or password == 'Q':
                break
            elif password != user_info[username]['password'] and count < 3:
                password = getpass.getpass('%s密码错误，您还可以尝试%s次，请重新输入您的密码，或输入"q"退出：%s'.strip()
                                           % (color_red, 3 - count, color_end))
                count += 1
            elif password != user_info[username]['password'] and count == 3:
                if username != 'administrator':
                    user_info[username]['status'] = 'lock'
                    print('%s密码错误次数达到3次，用户被锁定，请联系管理员解锁！%s' % (color_red, color_end))
                    break
                else:
                    print('%s密码错误次数达到3次，请稍后再试！%s' % (color_red, color_end))
                    break
            else:
                login_status = 'success'
                return login_status


def password_modify(username):
    # 用户登录成功后，修改密码
    while True:
        password1 = getpass.getpass('请输入您的密码，或输入"q"退出：').strip()
        if password1 != 'q' and password1 != 'Q':
            password1 = password_check(password1)
            if password1 is not None:
                password2 = getpass.getpass('请再次输入您的密码：').strip()
            else:
                break
        else:
            break
        if password1 == password2:
            with shelve.open('.user_info', writeback=True) as user_info:
                user_info[username]['password'] = password1
            print('%s密码修改成功，请重新登录！%s' % (color_green, color_end))
            password_modify_status = 'success'
            return password_modify_status
        else:
            print('%s两次输入的密码不一致，请重新输入！%s' % (color_red, color_end))


def user_delete():
    username = input('请输入要删除的用户名，或输入"q"退出：').strip()
    if username != 'q' or username != 'Q':
        with shelve.open('.user_info') as user_info:
            while True:
                if username == 'q' or username == 'Q':
                    break
                elif username == 'administrator':
                    username = input('%s管理员用户不能删除，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
                elif username not in user_info:
                    username = input('%s该用户名不存在，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
                else:
                    user_choice = input('输入"y"确认删除，输入"n"取消删除，请输入您的选择：').strip()
                    user_choice = user_choice_check(user_choice, 'Y', 'y', 'N', 'n')
                    if user_choice == 'Y' or user_choice == 'y':
                        user_info.pop(username)
                        print('%s删除成功，请进行其它操作！%s' % (color_green, color_end))
                        break
                    else:
                        break


def user_unlock():
    username = input('请输入要解锁的用户名，或输入"q"退出：').strip()
    if username != 'q' or username != 'Q':
        with shelve.open('.user_info', writeback=True) as user_info:
            while True:
                if username == 'q' or username == 'Q':
                    break
                elif username not in user_info:
                    username = input('%s用户名不存在，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
                elif user_info[username]['status'] == 'unlock':
                    username = input('%s该用户未被锁定，请重新输入，或输入"q"退出：%s' % (color_red, color_end)).strip()
                else:
                    user_choice = input('输入"y"确认解锁，输入"n"取消解锁，请输入您的选择：').strip()
                    user_choice = user_choice_check(user_choice, 'Y', 'y', 'N', 'n')
                    if user_choice == 'Y' or user_choice == 'y':
                        user_info[username]['status'] = 'unlock'
                        print('%s用户%s解锁成功成功，请进行其它操作！%s' % (color_green, username, color_end))
                        break
                    else:
                        break


def user_info_list():
    print('%s--------------------------------------------------' % color_green)
    print('%-20s%-10s%-20s' % ('Username', 'Status', 'Register_time'))
    print('-' * 50)
    with shelve.open('.user_info') as user_info:
        for username in user_info:
            print('%-20s%-10s%-20s' % (username, user_info[username]['status'], user_info[username]['register_time']))
    print('--------------------------------------------------%s' % color_end)


def user_register():
    # 用户注册
    username = input('请输入您的用户名，或输入"q"退出：').strip()
    if username != 'q' and username != 'Q':
        username = user_register_username_check(username)
        if username is not None:
            while True:
                password1 = getpass.getpass('请输入您的密码，或输入"q"退出：').strip()
                if password1 != 'q' and password1 != 'Q':
                    password1 = password_check(password1)
                    if password1 is not None:
                        password2 = getpass.getpass('请再次输入您的密码：').strip()
                    else:
                        break
                else:
                    break
                if password1 == password2:
                    with shelve.open('.user_info') as user_info:
                        user_info[username] = {'password': password1,
                                               'status': 'unlock',
                                               'register_time': timestamp()}
                    print('%s注册成功，请继续继续其它操作！%s' % (color_green, color_end))
                    break
                else:
                    print('%s两次输入的密码不一致，请重新输入！%s' % (color_red, color_end))


def user_login():
    # 普通用户登录
    username = input('请输入您的用户名，或输入"q"退出：').strip()
    if username != 'q' and username != 'Q':
        username = user_login_username_check(username)
        if username is not None:
            password = getpass.getpass('请输入您的密码，或输入"q"退出：').strip()
            if password != 'q' and password != 'Q':
                login_status = login_status_check(username, password)
                if login_status == 'success':
                    if username != 'administrator':
                        print('%s登录成功，您的身份是普通用户，请继续继续其它操作！%s' % (color_green, color_end))
                        while True:
                            print(user_login_menu)
                            user_choice = input('请输入您的选择：').strip()
                            user_choice = user_choice_check(user_choice, '1', '2', '3')
                            if user_choice == '1':
                                password_modify_status = password_modify(username)
                                if password_modify_status == 'success':
                                    break
                            elif user_choice == '2':
                                break
                            else:
                                exit('%s感谢您的使用！%s' % (color_green, color_end))
                    else:
                        print('%s登录成功，您的身份是管理员，请继续继续其它操作！%s' % (color_green, color_end))
                        while True:
                            print(admin_login_menu)
                            user_choice = input('请输入您的选择：').strip()
                            user_choice = user_choice_check(user_choice, '1', '2', '3', '4', '5', '6')
                            if user_choice == '1':
                                password_modify_status = password_modify(username)
                                if password_modify_status == 'success':
                                    break
                            elif user_choice == '2':
                                user_delete()
                            elif user_choice == '3':
                                user_unlock()
                            elif user_choice == '4':
                                user_info_list()
                            elif user_choice == '5':
                                break
                            else:
                                exit('%s感谢您的使用！%s' % (color_green, color_end))


def main():
    user_info_file_check()
    while True:
        print(main_menu)
        user_choice = input('请输入您的选择：').strip()
        user_choice = user_choice_check(user_choice, '1', '2', '3')
        if user_choice == '1':
            user_register()
        elif user_choice == '2':
            user_login()
        else:
            exit('%s感谢您的使用！%s' % (color_green, color_end))


if __name__ == "__main__":
    main()
