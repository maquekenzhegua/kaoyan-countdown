package io.github.maquekenzhegua.kaoyan;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONObject;

import java.util.Calendar;

/** 每日提醒:触发时实时计算剩余天数并推送通知,然后安排下一天。 */
public class DayReminderReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        JSONObject d = ReminderScheduler.nativeData(context);
        if (!d.optBoolean("remind", false)) {
            ReminderScheduler.reschedule(context);
            return;
        }
        if (Build.VERSION.SDK_INT >= 33
                && ContextCompat.checkSelfPermission(context, android.Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            ReminderScheduler.reschedule(context);
            return;
        }
        int days = daysUntil(d.optString("exam", "2027-12-18"));
        String ky = d.optString("ky", "2028");
        if (days < 0) {
            days = 0;
        }

        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        String channel = "daily_reminder";
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(channel,
                    context.getString(R.string.remind_channel_name), NotificationManager.IMPORTANCE_DEFAULT);
            nm.createNotificationChannel(ch);
        }
        String title = context.getString(R.string.remind_title_template)
                .replace("%1$s", ky)
                .replace("%2$d", String.valueOf(days));
        Intent open = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName());
        PendingIntent pi = PendingIntent.getActivity(context, 2001, open,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        android.app.Notification n = new NotificationCompat.Builder(context, channel)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle(title)
                .setContentText(context.getString(R.string.remind_text))
                .setAutoCancel(true)
                .setContentIntent(pi)
                .build();
        nm.notify(2101, n);
        ReminderScheduler.reschedule(context);
    }

    static int daysUntil(String ymd) {
        try {
            String[] p = ymd.split("-");
            Calendar ex = Calendar.getInstance();
            ex.clear();
            ex.set(Integer.parseInt(p[0]), Integer.parseInt(p[1]) - 1, Integer.parseInt(p[2]), 0, 0, 0);
            Calendar now = Calendar.getInstance();
            now.clear();
            now.set(now.get(Calendar.YEAR), now.get(Calendar.MONTH), now.get(Calendar.DAY_OF_MONTH), 0, 0, 0);
            return (int) Math.round((ex.getTimeInMillis() - now.getTimeInMillis()) / 86400000.0);
        } catch (Exception e) {
            return 0;
        }
    }
}
