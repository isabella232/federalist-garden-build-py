import requests_mock

from contextlib import ExitStack

from invoke import MockContext, Result

from tasks import (setup_node, run_federalist_script, setup_ruby,
                   build_jekyll, download_hugo, build_hugo, build_static)

from tasks.build import node_context

# TODO: use pyfakefs to setup PACKAGE_JSON_PATH, NVM_SH_PATH, etc
# so we can test those code paths


class TestSetupNode():
    def test_it_is_callable(self):
        ctx = MockContext(run=Result(''))
        setup_node(ctx)


class TestNodeContext():
    def test_default_node_context(self):
        ctx = MockContext()
        context_stack = node_context(ctx)
        assert type(context_stack) == ExitStack
        assert len(context_stack._exit_callbacks) == 1

    def test_node_context_accepts_more_contexts(self):
        ctx = MockContext()
        context_stack = node_context(ctx, ctx.cd('boop'))
        assert type(context_stack) == ExitStack
        assert len(context_stack._exit_callbacks) == 2


class TestRunFederalistScript():
    def test_it_is_callable(self):
        ctx = MockContext()
        run_federalist_script(ctx, branch='branch', owner='owner',
                              repository='repo', site_prefix='site/prefix',
                              base_url='/site/prefix')


class TestSetupRuby():
    def test_it_is_callable(self):
        ctx = MockContext(run=Result('ruby -v result'))
        setup_ruby(ctx)


class TestBuildJekyll():
    def test_it_is_callable(self):
        ctx = MockContext(run=[
            Result('gem install jekyll result'),
            Result('jekyll version result'),
            Result('jekyll build result'),
        ])
        build_jekyll(ctx, branch='branch', owner='owner',
                     repository='repo', site_prefix='site/prefix',
                     config='boop: beep', base_url='/site/prefix')


class TestDownloadHugo():
    def test_it_is_callable(self):
        ctx = MockContext(run=[
            Result('tar result'),
            Result('chmod result'),
        ])
        with requests_mock.Mocker() as m:
            m.get(
                'https://github.com/gohugoio/hugo/releases/download'
                '/v0.23/hugo_0.23_Linux-64bit.tar.gz')
            download_hugo(ctx)

    def test_it_accepts_other_versions(self):
        ctx = MockContext(run=[
            Result('tar result'),
            Result('chmod result'),
        ])
        with requests_mock.Mocker() as m:
            m.get(
                'https://github.com/gohugoio/hugo/releases/download'
                '/v0.25/hugo_0.25_Linux-64bit.tar.gz')
            download_hugo(ctx, version='0.25')


class TestBuildHugo():
    def test_it_is_callable(self):
        ctx = MockContext(run=[
            Result('tar result'),
            Result('chmod result'),
            Result('hugo version result'),
            Result('hugo build result'),
        ])
        with requests_mock.Mocker() as m:
            m.get(
                'https://github.com/gohugoio/hugo/releases/download'
                '/v0.23/hugo_0.23_Linux-64bit.tar.gz')
            build_hugo(ctx, branch='branch', owner='owner',
                       repository='repo', site_prefix='site/prefix',
                       base_url='/site/prefix', hugo_version='0.23')


class TestBuildstatic():
    def test_it_is_callable(self):
        ctx = MockContext()
        build_static(ctx)
