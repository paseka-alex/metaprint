from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from tgbot.localisations.i18nCustomManager import RedisLocManager


i18n_middleware = I18nMiddleware(core=FluentRuntimeCore(path="tgbot/localisations/locals/{locale}"), manager=RedisLocManager(), default_locale="uk")