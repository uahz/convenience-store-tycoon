package tycoon.ui

import androidx.compose.runtime.Composable

/** 各平台演示钩子：仅桌面端实现自动演示与自截画面。 */
@Composable
expect fun DemoHook(vm: GameViewModel)
