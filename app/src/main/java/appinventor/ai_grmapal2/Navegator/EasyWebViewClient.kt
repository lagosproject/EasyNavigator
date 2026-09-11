package appinventor.ai_grmapal2.Navegator

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

class EasyWebViewClient(
    private val context: Context,
    private val onPageStartedCallback: (url: String) -> Unit,
    private val onPageFinishedCallback: (url: String, canGoBack: Boolean, canGoForward: Boolean) -> Unit,
    private val onErrorCallback: (description: String) -> Unit
) : WebViewClient() {

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        url?.let { onPageStartedCallback(it) }
    }

    override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        if (view != null && url != null) {
            onPageFinishedCallback(url, view.canGoBack(), view.canGoForward())
        }
    }

    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
        val uri = request?.url ?: return false
        val scheme = uri.scheme?.lowercase() ?: return false

        return if (scheme == "http" || scheme == "https" || scheme == "about") {
            false
        } else {
            handleExternalUri(uri)
        }
    }

    @Deprecated("Deprecated in Java")
    override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
        if (url == null) return false
        val uri = Uri.parse(url)
        val scheme = uri.scheme?.lowercase() ?: return false

        return if (scheme == "http" || scheme == "https" || scheme == "about") {
            false
        } else {
            handleExternalUri(uri)
        }
    }

    private fun handleExternalUri(uri: Uri): Boolean {
        return try {
            val intent = Intent(Intent.ACTION_VIEW, uri).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            true
        } catch (e: Exception) {
            false
        }
    }

    override fun onReceivedError(
        view: WebView?,
        request: WebResourceRequest?,
        error: WebResourceError?
    ) {
        super.onReceivedError(view, request, error)
        if (request?.isForMainFrame == true) {
            val desc = error?.description?.toString() ?: "Network error"
            onErrorCallback(desc)
        }
    }
}
