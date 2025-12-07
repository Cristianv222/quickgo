// src/components/restaurants/RestaurantSchedule.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Schedule } from '../../api/restaurants';

interface RestaurantScheduleProps {
  schedules: Schedule[];
}

const RestaurantSchedule: React.FC<RestaurantScheduleProps> = ({ schedules }) => {
  // Ordenar por día de la semana
  const sortedSchedules = [...schedules].sort((a, b) => a.day_of_week - b.day_of_week);

  return (
    <View style={styles.container}>
      {sortedSchedules.map((schedule) => (
        <View key={schedule.id} style={styles.row}>
          <Text style={styles.day}>{schedule.day_name}</Text>
          {schedule.is_closed ? (
            <Text style={styles.closed}>Cerrado</Text>
          ) : (
            <Text style={styles.hours}>
              {schedule.opening_time.slice(0, 5)} - {schedule.closing_time.slice(0, 5)}
            </Text>
          )}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
  },
  day: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  hours: {
    fontSize: 14,
    color: '#666',
  },
  closed: {
    fontSize: 14,
    color: '#FF6B6B',
    fontStyle: 'italic',
  },
});

export default RestaurantSchedule;