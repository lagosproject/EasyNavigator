package appinventor.ai_grmapal2.Navegator

import android.content.Context
import android.content.SharedPreferences
import android.util.Patterns
import java.net.URLEncoder
import java.nio.charset.StandardCharsets
import java.util.regex.Pattern

class SearchEngineManager(context: Context) {

    enum class Engine(val displayName: String, val queryTemplate: String) {
        GOOGLE("Google", "https://www.google.com/search?q=%s"),
        DUCKDUCKGO("DuckDuckGo", "https://duckduckgo.com/?q=%s"),
        BING("Bing", "https://www.bing.com/search?q=%s"),
        ECOSIA("Ecosia", "https://www.ecosia.org/search?q=%s"),
        CUSTOM("Custom", "")
    }

    private val prefs: SharedPreferences =
        context.getSharedPreferences("easy_navigator_settings", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_ENGINE = "search_engine_type"
        private const val KEY_CUSTOM_URL = "custom_search_engine_url"
        private val DOMAIN_REGEX = Pattern.compile(
            "^(https?://)?([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,}(:\\d+)?(/.*)?$"
        )
        private val IP_REGEX = Pattern.compile(
            "^(https?://)?(\\d{1,3}\\.){3}\\d{1,3}(:\\d+)?(/.*)?$"
        )
    }

    var selectedEngine: Engine
        get() {
            val name = prefs.getString(KEY_ENGINE, Engine.GOOGLE.name) ?: Engine.GOOGLE.name
            return try {
                Engine.valueOf(name)
            } catch (e: Exception) {
                Engine.GOOGLE
            }
        }
        set(value) {
            prefs.edit().putString(KEY_ENGINE, value.name).apply()
        }

    var customEngineUrl: String
        get() = prefs.getString(KEY_CUSTOM_URL, "") ?: ""
        set(value) {
            prefs.edit().putString(KEY_CUSTOM_URL, value).apply()
        }

    fun buildUrlOrSearch(input: String): String {
        val trimmed = input.trim()
        if (trimmed.isEmpty()) {
            return getHomeUrl()
        }

        // Check if already starts with a recognized scheme
        if (trimmed.startsWith("http://", ignoreCase = true) ||
            trimmed.startsWith("https://", ignoreCase = true) ||
            trimmed.startsWith("file://", ignoreCase = true) ||
            trimmed.startsWith("about:", ignoreCase = true)
        ) {
            return trimmed
        }

        // Check if it has spaces; if so, it is almost certainly a search query
        if (trimmed.contains(" ")) {
            return buildSearchQueryUrl(trimmed)
        }

        // Check if matches domain or IP pattern
        if (DOMAIN_REGEX.matcher(trimmed).matches() ||
            IP_REGEX.matcher(trimmed).matches() ||
            Patterns.WEB_URL.matcher("https://$trimmed").matches()
        ) {
            return "https://$trimmed"
        }

        return buildSearchQueryUrl(trimmed)
    }

    fun buildSearchQueryUrl(query: String): String {
        val encoded = try {
            URLEncoder.encode(query, StandardCharsets.UTF_8.name())
        } catch (e: Exception) {
            query
        }

        return when (val engine = selectedEngine) {
            Engine.CUSTOM -> {
                val template = customEngineUrl
                if (template.contains("%s")) {
                    template.replace("%s", encoded)
                } else {
                    Engine.GOOGLE.queryTemplate.replace("%s", encoded)
                }
            }
            else -> engine.queryTemplate.replace("%s", encoded)
        }
    }

    fun getHomeUrl(): String {
        return when (selectedEngine) {
            Engine.DUCKDUCKGO -> "https://duckduckgo.com"
            Engine.BING -> "https://www.bing.com"
            Engine.ECOSIA -> "https://www.ecosia.org"
            Engine.CUSTOM -> {
                val template = customEngineUrl
                if (template.isNotBlank()) {
                    template.substringBefore("?")
                } else {
                    "https://www.google.com"
                }
            }
            else -> "https://www.google.com"
        }
    }
}
