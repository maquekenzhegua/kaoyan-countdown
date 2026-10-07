package io.github.maquekenzhegua.kaoyan;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import org.json.JSONObject;

import java.util.Calendar;

/** 读取 JS 侧写入的 CapacitorStorage 偏好,安排每日提醒闹钟。 */
public class ReminderScheduler {

    static final String PREF_FILE = "CapacitorStorage";
    static final String DATA_KEY = "ky_native";
    static final int ALARM_RC = 1001;

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREF_FILE, Context.MODE_PRIVATE);
    }

    static JSONObject nativeData(Context c) {
        try {
            String s = prefs(c).getString(DATA_KEY, null);
            if (s != null) return new JSONObject(s);
        } catch (Exception ignored) {
        }
        return new JSONObject();
    }

    /** 每次打开 App / 开机 / 修改设置时调用,保证闹钟指向下一次提醒时间。 */
    public static void reschedule(Context c) {
        JSONObject d = nativeData(c);
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        Intent it = new Intent(c, DayReminderReceiver.class);
        PendingIntent pi = PendingIntent.getBroadcast(c, ALARM_RC, it,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        am.cancel(pi);
        if (!d.optBoolean("remind", false)) return;

        int h = 8, m = 0;
        try {
            String[] p = d.optString("remindTime", "08:00").split(":");
            h = Integer.parseInt(p[0]);
            m = Integer.parseInt(p[1]);
        } catch (Exception ignored) {
        }
        Calendar cal = Calendar.getInstance();
        cal.set(Calendar.HOUR_OF_DAY, h);
        cal.set(Calendar.MINUTE, m);
        cal.set(Calendar.SECOND, 0);
        cal.set(Calendar.MILLISECOND, 0);
        if (cal.getTimeInMillis() <= System.currentTimeMillis()) {
            cal.add(Calendar.DAY_OF_YEAR, 1);
        }
        boolean canExact = Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms();
        if (canExact) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), pi);
        } else {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), pi);
        }
    }
}
