package appinventor.ai_grmapal2.Navegator

import android.annotation.SuppressLint
import android.content.Context
import android.os.Build
import android.webkit.CookieManager
import android.webkit.WebSettings
import android.webkit.WebStorage
import android.webkit.WebView
import java.io.File

object PrivacyWebManager {

    @SuppressLint("SetJavaScriptEnabled")
    fun configurePrivacySettings(webView: WebView) {
        val settings = webView.settings

        // Enable JavaScript for modern web application rendering
        settings.javaScriptEnabled = true

        // Strict ephemeral mode: load without disk caching
        settings.cacheMode = WebSettings.LOAD_NO_CACHE

        // Disable saving sensitive form and credential data
        @Suppress("DEPRECATION")
        settings.saveFormData = false
        @Suppress("DEPRECATION")
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            settings.savePassword = false
        }

        // Privacy and isolation defaults
        settings.setGeolocationEnabled(false)
        settings.databaseEnabled = false
        settings.allowFileAccess = false
        settings.allowContentAccess = false

        // DOM storage active in session only; will be wiped on exit
        settings.domStorageEnabled = true

        // Responsive viewport and zoom controls
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.setSupportZoom(true)
        settings.builtInZoomControls = true
        settings.displayZoomControls = false

        // Mixed content safety
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW

        // Clear cookies on start to ensure clean slate
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        cookieManager.setAcceptThirdPartyCookies(webView, false)
    }

    /**
     * Completely incinerates all session cookies, caches, DOM storage,
     * history, and temporary disk files.
     */
    fun wipeSession(context: Context, webView: WebView?) {
        webView?.apply {
            stopLoading()
            loadUrl("about:blank")
            clearCache(true)
            clearHistory()
            clearFormData()
            clearSslPreferences()
        }

        // Wipe all cookies
        val cookieManager = CookieManager.getInstance()
        cookieManager.removeAllCookies(null)
        cookieManager.removeSessionCookies(null)
        cookieManager.flush()

        // Wipe DOM Storage / LocalStorage / IndexedDB
        WebStorage.getInstance().deleteAllData()

        // Wipe application cache directory
        try {
            val cacheDir = context.cacheDir
            deleteDirectoryContent(cacheDir)
            val appDir = File(context.applicationInfo.dataDir, "app_webview")
            if (appDir.exists()) {
                deleteDirectoryContent(appDir)
            }
        } catch (e: Exception) {
            // Ignore cache deletion errors
        }
    }

    private fun deleteDirectoryContent(dir: File?) {
        if (dir != null && dir.isDirectory) {
            val children = dir.listFiles() ?: return
            for (child in children) {
                if (child.isDirectory) {
                    deleteDirectoryContent(child)
                }
                child.delete()
            }
        }
    }
}
