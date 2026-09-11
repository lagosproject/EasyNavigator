package appinventor.ai_grmapal2.Navegator

import android.webkit.WebChromeClient
import android.webkit.WebView

class EasyWebChromeClient(
    private val onProgressUpdate: (progress: Int) -> Unit,
    private val onTitleReceived: (title: String) -> Unit
) : WebChromeClient() {

    override fun onProgressChanged(view: WebView?, newProgress: Int) {
        super.onProgressChanged(view, newProgress)
        onProgressUpdate(newProgress)
    }

    override fun onReceivedTitle(view: WebView?, title: String?) {
        super.onReceivedTitle(view, title)
        title?.let { onTitleReceived(it) }
    }
}
