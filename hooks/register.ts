import type { Register } from 'claude-code'

const NAME = 'plugin-usage'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: NAME,
      description: '플러그인별 사용 횟수와 안 쓴 플러그인(삭제 후보)을 보여줘요. 예: /plugin-usage 30',
    })
    return next(e)
  })

  on('command.run', { command: NAME }, async ($, e) => {
    const arg = e.args.trim()
    const days = /^\d+$/.test(arg) ? arg : '30'
    const script = `${$.plugin.root}/scripts/scan.py`
    try {
      const ran = await $.process.run(['python', '-X', 'utf8', '-I', script, days])
      if (ran.exitCode !== 0) {
        return { text: `집계 중 오류가 났어요:\n${ran.stderr.slice(-1500)}` }
      }
      return { text: ran.stdout.trim(), isTextDisplayOnly: true }
    } catch (err) {
      return { text: `파이썬을 실행하지 못했어요: ${String(err)}` }
    }
  })
}
