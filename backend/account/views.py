# polls/views.py

from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm


from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import (authenticate, login,  logout, update_session_auth_hash, get_user)
from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm)
from django.contrib.auth.decorators import login_required

# Create your views here.


def create(request):
    if request.method == "GET":
        # Form객체를 context value로 전달.
        return render(
            request,
            "account/create.html",
            {"form": CustomUserCreationForm()}
        )

    elif request.method == "POST":
        # 가입처리

        form = CustomUserCreationForm(request.POST, request.FILES)

        if form.is_valid():  # 요청파라미터에 문제가 없는 경우 DB에 저장
            user = form.save()
            print(type(user), user)


            return redirect(reverse("chat:welcome"))

        else:  # 요청파라미터에 문제가 있는 경우.
            return render(
                request,
                "account/create.html",
                {"form": form}
            )


# 가입한 사용자 정보 조회
# URL: /account/detail
# 함수: detail
# 응답: account/detail.html

@login_required
def detail(request):
    try:
        # 로그인한 사용자의 user로 부터 id를 조회
        # get_user(request)/request.user: 로그인한 User 모델 객체
        user_id = get_user(request).pk
        user = CustomUser.objects.get(pk=user_id)
        return render(
            request, "account/detail.html", {"user": user}
        )

    except:
        return render(request, "error.html", {"error_message": "회원정보 조회 도중 문제가 발생."})


# 로그인처리
# 요청URL: /account/login
# 함수: user_login

def user_login(request):
    if request.method == "GET":
        return render(
            request,
            "account/login.html",
            {"form": AuthenticationForm()}
        )

    elif request.method == "POST":
        # 로그인 처리
        ## 요청파라미터(username, password) 조회
        username = request.POST['username']
        password = request.POST['password']

        ## DB로 부터 조회(username과 password가 일치하는지)
        ### 반환: User Model(일치), None (불일치)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            ## 일치 - 로그인 처리(session에 로그인 사용자 정보-UserModel-을 저장)
            login(request, user)  # session에 user를 등록


            if request.GET.get("next"):  # next 쿼리스트링이 있다면
                return redirect(request.GET.get("next"))

            return redirect(reverse("chat:welcome"))
        else:
            ## 불일치- 로그인 화면으로 이동
            return render(
                request,
                "account/login.html",
                {"form": AuthenticationForm(),
                 "error_msg": "username, password를 다시 확인하세요."}

            )


# 로그아웃 처리
@login_required
def user_logout(request):
    # 로그인시 호출했던 login() 함수가 처리한 것을 무효화 처리(session에서 user정보를 제거)
    logout(request)
    return redirect(reverse("chat:welcome"))


# 로그인한 회원정보 수정
@login_required
def update(request):
    if request.method == "GET":
        # CustomUserChangeForm 을 이용
        ## 수정 폼: 객체 생성시 수정할 Model객체를 전달.
        form = CustomUserChangeForm(instance=get_user(request))
        return render(request, "account/update.html", {"form": form})

    elif request.method == "POST":
        # 수정 처리
        # 1. 요청파라미터 조회 + 검증
        form = CustomUserChangeForm(request.POST, request.FILES, instance=get_user(request))

        if form.is_valid():
            # DB에 저장
            user = form.save()
            # session의 저장된  User정보를 수정된 것으로 변경.
            update_session_auth_hash(request, user)
            # 상세페이지 요청
            return redirect(reverse("account:detail"))
        else:
            return render(request, "account/update.html", {"form": form})


# Password 변경 처리
# 요청 URL: /account/password_change
# view함수: password_change
# 처리 - GET: 패스워드 변경 폼 페이지 이동( account/password_change.html )
#       Post: 패스워드 변경 처리 (redirect - account:detail)
@login_required
def password_change(request):
    if request.method == "GET":
        form = PasswordChangeForm(get_user(request))  # User Model을 넣어서 생성
        return render(request, "account/password_change.html", {"form": form})

    elif request.method == "POST":
        # 요청파라미터 조회 + 검증
        form = PasswordChangeForm(get_user(request), request.POST)
        if form.is_valid():
            # DB에 저장.
            user = form.save()
            update_session_auth_hash(request, user)
            # 응답
            return redirect(reverse("account:detail"))
        else:
            return render(request, "account/password_change.html", {"form": form})


# 사용자 삭제(탈퇴) 처리
# 요청 URL: /account/delete
# view함수: user_delete
# 응답: redirect - chat:welcome
@login_required
def user_delete(request):
    # 로그인 한 사용자를 삭제
    user = get_user(request)  # 로그인한 사용자 Model
    user.delete()  # DB 에서 삭제
    # 로그아웃 처리
    logout(request)
    return redirect(reverse("chat:welcome"))