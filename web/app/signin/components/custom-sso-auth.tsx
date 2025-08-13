import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'next/navigation'
import Button from '@/app/components/base/button'
import { API_PREFIX } from '@/config'
import { getPurifyHref } from '@/utils'
import { Lock01 } from '@/app/components/base/icons/src/vender/solid/security'

type CustomSSOAuthProps = {
  disabled?: boolean
}

export default function CustomSSOAuth(props: CustomSSOAuthProps) {
  const { t } = useTranslation()
  const searchParams = useSearchParams()

  const getSSOLink = () => {
    const url = getPurifyHref(`${API_PREFIX}/oauth/login/sso`)
    if (searchParams.has('invite_token'))
      return `${url}?${searchParams.toString()}`

    return url
  }

  return (
    <div className='w-full'>
      <a href={getSSOLink()}>
        <Button
          disabled={props.disabled}
          className='w-full'
        >
          <Lock01 className='mr-2 h-5 w-5 text-text-accent-light-mode-only' />
          <span className="truncate leading-normal">{t('login.withSSO')}</span>
        </Button>
      </a>
    </div>
  )
}
